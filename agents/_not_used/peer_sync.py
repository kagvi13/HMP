# agent/peer_sync.py

import socket
import json
import time
import threading
import select
import netifaces
import re
import ipaddress
import asyncio
import dateutil.parser

from datetime import datetime, timezone as UTC
from tools.storage import Storage

storage = Storage()

# ---------------------------
# Конфигурация (будем пересчитывать после bootstrap)
# ---------------------------
my_id = storage.get_config_value("agent_id")
agent_name = storage.get_config_value("agent_name", "unknown")

# placeholders — реальные значения пересчитаются в start_sync()
local_addresses = []
global_addresses = []
all_addresses = []
local_ports = []
print(f"[PeerSync] (init) my_id={my_id} name={agent_name}")

# ---------------------------
# Загрузка bootstrap
# ---------------------------
def load_bootstrap_peers(filename="bootstrap.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"[Bootstrap] File {filename} not found")
        return

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Разделяем строку на ключ:значение по ";"
        parts = [p.strip() for p in line.split(";") if p.strip()]
        data = {}
        for part in parts:
            if ":" not in part:
                continue
            key, val = part.split(":", 1)
            key = key.strip().upper()
            val = val.strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1].replace("\\n", "\n")
            data[key] = val

        # Проверка обязательных полей
        did = data.get("DID")
        pubkey = data.get("KEY")
        addresses_json = data.get("ADDRESS")
        name = data.get("NAME")

        if not did or not pubkey or not addresses_json:
            print(f"[Bootstrap] Missing required fields in line: {line}")
            continue

        # Парсим адреса
        try:
            addresses = json.loads(addresses_json)
        except Exception as e:
            print(f"[Bootstrap] Failed to parse JSON addresses: {line} ({e})")
            continue

        # Расширяем any:// в tcp/udp и приводим к формату адресов
        expanded_addresses = []
        for addr in addresses:
            if isinstance(addr, dict):
                # старый формат с address/pow → конвертим
                if "address" in addr:
                    addr_str = addr["address"]
                    if addr_str.startswith("any://"):
                        hostport = addr_str[len("any://"):]
                        variants = [f"tcp://{hostport}", f"udp://{hostport}"]
                    else:
                        variants = [addr_str]

                    for v in variants:
                        expanded_addresses.append({
                            "addr": v,
                            "nonce": addr.get("pow", {}).get("nonce"),
                            "pow_hash": addr.get("pow", {}).get("hash"),
                            "difficulty": addr.get("pow", {}).get("difficulty"),
                            "datetime": addr.get("datetime", "")
                        })
                # уже новый формат → оставляем как есть
                elif "addr" in addr:
                    expanded_addresses.append(addr)

            elif isinstance(addr, str):
                if addr.startswith("any://"):
                    hostport = addr[len("any://"):]
                    expanded_addresses.extend([
                        {"addr": f"tcp://{hostport}", "nonce": None, "pow_hash": None, "difficulty": None, "datetime": ""},
                        {"addr": f"udp://{hostport}", "nonce": None, "pow_hash": None, "difficulty": None, "datetime": ""}
                    ])
                else:
                    expanded_addresses.append({
                        "addr": addr,
                        "nonce": None,
                        "pow_hash": None,
                        "difficulty": None,
                        "datetime": ""
                    })

        # Сохраняем в storage
        print(f"[DEBUG] Saving peer {did} with addresses:")
        for a in expanded_addresses:
            print(a)
        storage.add_or_update_peer(
            peer_id=did,
            name=name,
            addresses=expanded_addresses,
            source="bootstrap",
            status="offline",
            pubkey=pubkey,
            capabilities=None,
            heard_from=None
        )

        print(f"[Bootstrap] Loaded peer {did} -> {expanded_addresses}")

# ---------------------------
# UDP Discovery
# ---------------------------
def udp_discovery():
    import dateutil.parser  # для парсинга ISO datetime
    DISCOVERY_INTERVAL = 30

    try:
        # --- Создаём слушающие сокеты один раз (на основе текущих локальных адресов в storage) ---
        listen_sockets = []
        cfg_local_addresses = storage.get_config_value("local_addresses", [])
        print(f"[UDP Discovery] Local addresses (init): {cfg_local_addresses}")

        for entry in cfg_local_addresses:
            addr_str = entry.get("addr") if isinstance(entry, dict) else entry
            if not addr_str:
                continue

            proto, hostport = addr_str.split("://", 1)
            host, port = storage.parse_hostport(hostport)
            if not port or proto.lower() != "udp":
                continue

            # IPv4
            if not host.startswith("["):
                try:
                    sock4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock4.bind(("", port))
                    listen_sockets.append(sock4)
                    print(f"[UDP Discovery] Listening IPv4 on *:{port}")
                except Exception as e:
                    print(f"[UDP Discovery] IPv4 bind failed on port {port}: {e}")

            # IPv6
            else:
                try:
                    sock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                    sock6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock6.bind(("::", port))
                    listen_sockets.append(sock6)
                    print(f"[UDP Discovery] Listening IPv6 on [::]:{port}")
                except Exception as e:
                    print(f"[UDP Discovery] IPv6 bind failed on port {port}: {e}")

    except Exception as init_e:
        print(f"[UDP Discovery] init error: {init_e}")
        return

    # --- Основной цикл ---
    while True:
        try:
            agent_pubkey = storage.get_config_value("agent_pubkey")

            # Приём входящих пакетов
            if listen_sockets:
                rlist, _, _ = select.select(listen_sockets, [], [], 0.5)
                for sock in rlist:
                    try:
                        data, addr = sock.recvfrom(2048)
                        print(f"[UDP Discovery] RAW from {addr}: {data!r}")

                        try:
                            msg = json.loads(data.decode("utf-8"))
                        except Exception as e:
                            print(f"[UDP Discovery] JSON decode error from {addr}: {e}")
                            continue

                        peer_id = msg.get("id")
                        if peer_id == my_id:
                            continue
                        name = msg.get("name", "unknown")
                        addresses = msg.get("addresses", []) or []

                        valid_addresses = []
                        for a in addresses:
                            addr_str = a.get("addr")
                            nonce = a.get("nonce")
                            pow_hash = a.get("pow_hash")
                            difficulty = a.get("difficulty")
                            dt = a.get("datetime")
                            pubkey = a.get("pubkey")

                            if not addr_str:
                                continue

                            # нормализуем адрес (везде используем единый формат)
                            addr_norm = storage.normalize_address(addr_str)
                            if not addr_norm:
                                print(f"[UDP Discovery] Can't normalize addr {addr_str}, skip")
                                continue

                            # Проверка PoW — только если есть все поля
                            if nonce is not None and pow_hash and difficulty is not None:
                                if not pubkey:
                                    print(f"[UDP Discovery] Peer {peer_id} addr {addr_norm} missing pubkey, skip PoW check")
                                    continue
                                ok = storage.verify_pow(peer_id, pubkey, addr_norm, nonce, pow_hash, dt, difficulty)
                                print(f"[UDP Discovery] Verify PoW for {addr_norm} = {ok}")
                                if not ok:
                                    continue

                            # Проверка datetime
                            existing = storage.get_peer_address(peer_id, addr_norm)
                            try:
                                existing_dt = dateutil.parser.isoparse(existing.get("datetime")) if existing else None
                                dt_obj = dateutil.parser.isoparse(dt) if dt else None
                            except Exception as e:
                                print(f"[UDP Discovery] datetime parse error: {e}")
                                continue

                            if existing_dt and dt_obj and existing_dt >= dt_obj:
                                print(f"[UDP Discovery] Skip {addr_norm}: old datetime {dt}")
                                continue

                            # if all checks OK, ensure we keep canonical form in the stored dict
                            a_copy = dict(a)
                            a_copy["addr"] = addr_norm
                            valid_addresses.append(a_copy)

                        if valid_addresses:
                            storage.add_or_update_peer(
                                peer_id=peer_id,
                                name=name,
                                addresses=valid_addresses,
                                source="discovery",
                                status="online"
                            )
                            print(f"[UDP Discovery] Accepted peer {peer_id} ({addr}), {len(valid_addresses)} addresses")

                    except Exception as e:
                        print(f"[UDP Discovery] receive error: {e}")

            # --- Отправка broadcast/multicast ---
            # берем текущие локальные адреса из storage (актуально)
            cfg_local_addresses = storage.get_config_value("local_addresses", [])
            valid_local_addresses = []

            for a in cfg_local_addresses:
                addr_str = a.get("addr") if isinstance(a, dict) else a
                nonce = a.get("nonce") if isinstance(a, dict) else None
                pow_hash = a.get("pow_hash") if isinstance(a, dict) else None
                difficulty = a.get("difficulty") if isinstance(a, dict) else None
                dt = a.get("datetime") if isinstance(a, dict) else None
                # prefer explicit pubkey per-address, otherwise agent_pubkey
                addr_pubkey = a.get("pubkey") if isinstance(a, dict) else None
                pubkey_used = addr_pubkey or agent_pubkey

                if not addr_str:
                    continue

                addr_norm = storage.normalize_address(addr_str)
                if not addr_norm:
                    print(f"[UDP Discovery] Can't normalize local addr {addr_str}, skip")
                    continue

                # Проверка PoW только если есть необходимые поля
                if nonce is not None and pow_hash and difficulty is not None:
                    if not pubkey_used:
                        # если у агента нет pubkey в конфигах, не делаем жёсткую проверку PoW,
                        # потому что невозможно подтвердить — логируем и пропускаем проверку
                        print(f"[UDP Discovery] No pubkey for self addr {addr_norm}, skipping PoW self-check (will broadcast anyway)")
                        ok = True
                    else:
                        ok = storage.verify_pow(my_id, pubkey_used, addr_norm, nonce, pow_hash, dt, difficulty)
                        print(f"[UDP Discovery] Self-check PoW for {addr_norm} = {ok}")
                    if not ok:
                        print(f"[UDP Discovery] Self addr {addr_norm} failed PoW, skip")
                        continue

                # attach pubkey for broadcast so receivers can verify
                a_copy = dict(a) if isinstance(a, dict) else {"addr": addr_str}
                a_copy["addr"] = addr_norm
                if "pubkey" not in a_copy and agent_pubkey:
                    a_copy["pubkey"] = agent_pubkey
                valid_local_addresses.append(a_copy)

            msg_data = json.dumps({
                "id": my_id,
                "name": agent_name,
                "addresses": valid_local_addresses
            }).encode("utf-8")

            print(f"[UDP Discovery] Broadcasting: {msg_data}")

            for entry in valid_local_addresses:
                addr_str = entry.get("addr")
                proto, hostport = addr_str.split("://", 1)
                host, port = storage.parse_hostport(hostport)
                if not port or proto.lower() != "udp":
                    continue

                # IPv4 broadcast
                if not host.startswith("["):
                    for iface in netifaces.interfaces():
                        addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET, [])
                        for a in addrs:
                            if "broadcast" in a:
                                try:
                                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                                    print(f"[UDP Discovery] Sending broadcast -> {a['broadcast']}:{port}")
                                    sock.sendto(msg_data, (a["broadcast"], port))
                                    sock.close()
                                except Exception as e:
                                    print(f"[UDP Discovery] Broadcast error {a['broadcast']}:{port}: {e}")

                # IPv6 multicast ff02::1
                else:
                    for iface in netifaces.interfaces():
                        ifaddrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET6, [])
                        for a in ifaddrs:
                            addr_ipv6 = a.get("addr")
                            if not addr_ipv6:
                                continue
                            multicast_addr = f"ff02::1%{iface}" if addr_ipv6.startswith("fe80:") else "ff02::1"
                            try:
                                sock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                                sock6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_IF, socket.if_nametoindex(iface))
                                sock6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, 1)
                                print(f"[UDP Discovery] Sending multicast -> {multicast_addr}:{port}")
                                sock6.sendto(msg_data, (multicast_addr, port))
                                sock6.close()
                            except Exception as e:
                                print(f"[UDP Discovery] Multicast error {multicast_addr}:{port}: {e}")

            time.sleep(DISCOVERY_INTERVAL)

        except Exception as main_e:
            print(f"[UDP Discovery] main loop error: {main_e}")
            time.sleep(DISCOVERY_INTERVAL)

# ---------------------------
# TCP Peer Exchange (исходящие)
# ---------------------------
def tcp_peer_exchange():
    import dateutil.parser  # для корректного парсинга ISO datetime
    PEER_EXCHANGE_INTERVAL = 20  # секунды для отладки

    while True:
        # получаем свежий список пиров из БД
        peers = storage.get_known_peers(my_id, limit=50)
        print(f"[PeerExchange] Checking {len(peers)} peers (raw DB)...")

        for peer in peers:
            peer_id = peer["id"] if isinstance(peer, dict) else peer[0]
            addresses_json = peer["addresses"] if isinstance(peer, dict) else peer[1]

            if peer_id == my_id:
                continue

            try:
                addr_list = json.loads(addresses_json)
            except Exception as e:
                print(f"[PeerExchange] JSON decode error for peer {peer_id}: {e}")
                addr_list = []

            for addr_entry in addr_list:
                addr_str = addr_entry.get("addr")
                nonce = addr_entry.get("nonce")
                pow_hash = addr_entry.get("pow_hash")
                difficulty = addr_entry.get("difficulty")
                dt = addr_entry.get("datetime")
                pubkey = addr_entry.get("pubkey")

                # нормализация адреса (включая скобки IPv6 и т.п.)
                norm = storage.normalize_address(addr_str)
                if not norm:
                    continue

                # Проверка PoW
                if nonce is not None and pow_hash and difficulty is not None:
                    if not pubkey:
                        print(f"[PeerExchange] Peer {peer_id} addr {norm} missing pubkey, skip PoW check")
                        continue
                    ok = storage.verify_pow(peer_id, pubkey, norm, nonce, pow_hash, dt, difficulty)
                    print(f"[PeerExchange] Verify PoW for {peer_id}@{norm} = {ok}")
                    if not ok:
                        continue

                # Проверка datetime с использованием dateutil
                existing = storage.get_peer_address(peer_id, norm)
                try:
                    existing_dt = dateutil.parser.isoparse(existing.get("datetime")) if existing else None
                    dt_obj = dateutil.parser.isoparse(dt) if dt else None
                except Exception as e:
                    print(f"[PeerExchange] datetime parse error for {norm}: {e}")
                    continue

                if existing_dt and dt_obj and existing_dt >= dt_obj:
                    print(f"[PeerExchange] Skip {norm}: old datetime {dt}")
                    continue

                # Парсим host и port
                proto, hostport = norm.split("://", 1)
                if proto not in ["tcp", "any"]:
                    continue
                host, port = storage.parse_hostport(hostport)
                if not host or not port:
                    continue

                print(f"[PeerExchange] Trying {peer_id} at {host}:{port} (proto={proto})")

                try:
                    # IPv6 link-local
                    if storage.is_ipv6(host) and host.startswith("fe80:"):
                        scope_id = storage.get_ipv6_scope(host)
                        if scope_id is None:
                            print(f"[PeerExchange] Skipping {host}, no scope_id")
                            continue
                        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                        sock.settimeout(3)
                        sock.connect((host, port, 0, scope_id))
                    else:
                        sock = socket.socket(socket.AF_INET6 if storage.is_ipv6(host) else socket.AF_INET,
                                             socket.SOCK_STREAM)
                        sock.settimeout(3)
                        sock.connect((host, port))

                    # Получаем актуальные адреса на момент отправки (не использовать stale all_addresses)
                    cfg_local_addresses = storage.get_config_value("local_addresses", [])
                    cfg_global_addresses = storage.get_config_value("global_addresses", [])
                    cur_all_addresses = cfg_local_addresses + cfg_global_addresses

                    # Отправка handshake — фильтр адресов для public/private
                    if storage.is_private(host):
                        send_addresses = cur_all_addresses
                    else:
                        # фильтруем только публичные
                        send_addresses = []
                        for a in cur_all_addresses:
                            a_addr = a.get("addr") if isinstance(a, dict) else a
                            try:
                                host_only = storage.parse_hostport(a_addr.split("://", 1)[1])[0]
                                if is_public(host_only):
                                    send_addresses.append(a)
                            except Exception:
                                continue

                    handshake = {
                        "type": "PEER_EXCHANGE_REQUEST",
                        "id": my_id,
                        "name": agent_name,
                        "addresses": send_addresses,
                    }
                    raw_handshake = json.dumps(handshake).encode("utf-8")
                    print(f"[PeerExchange] Sending handshake -> {host}:{port}: {raw_handshake}")
                    sock.sendall(raw_handshake)

                    # Читаем ответ
                    data = sock.recv(64 * 1024)
                    sock.close()

                    if not data:
                        print(f"[PeerExchange] No data from {host}:{port}")
                        continue

                    print(f"[PeerExchange] RAW recv from {host}:{port}: {data!r}")

                    try:
                        peers_recv = json.loads(data.decode("utf-8"))
                        print(f"[PeerExchange] Parsed recv from {host}:{port}: {peers_recv}")
                        for p in peers_recv:
                            new_addrs = []
                            for a in p.get("addresses", []):
                                try:
                                    existing_addr = storage.get_peer_address(p["id"], a.get("addr"))
                                    existing_dt = dateutil.parser.isoparse(existing_addr.get("datetime")) if existing_addr else None
                                    dt_obj = dateutil.parser.isoparse(a.get("datetime")) if a.get("datetime") else None
                                    if existing_addr is None or (existing_dt and dt_obj and existing_dt < dt_obj) or existing_dt is None:
                                        new_addrs.append(a)
                                    else:
                                        print(f"[PeerExchange] Ignored old {a.get('addr')} from {p['id']}")
                                except Exception as e:
                                    print(f"[PeerExchange] Error parsing datetime for {a.get('addr')}: {e}")
                                    continue

                            if new_addrs:
                                storage.add_or_update_peer(
                                    p["id"],
                                    p.get("name", "unknown"),
                                    new_addrs,
                                    source="peer_exchange",
                                    status="online"
                                )
                                print(f"[PeerExchange] Stored {len(new_addrs)} new addrs for peer {p['id']}")
                        print(f"[PeerExchange] Received {len(peers_recv)} peers from {host}:{port}")
                    except Exception as e:
                        print(f"[PeerExchange] Decode error from {host}:{port}: {e}")
                        continue

                    break
                except Exception as e:
                    print(f"[PeerExchange] Connection to {host}:{port} failed: {e}")
                    continue

        time.sleep(PEER_EXCHANGE_INTERVAL)

# ---------------------------
# TCP Listener (входящие)
# ---------------------------
def tcp_listener():
    # получаем локальные порты в момент старта listener'а
    listen_sockets = []
    cfg_local_ports = storage.get_local_ports()
    print(f"[TCP Listener] binding to local ports: {cfg_local_ports}")
    for port in cfg_local_ports:
        for family, addr_str in [(socket.AF_INET, ""), (socket.AF_INET6, "::")]:
            try:
                sock = socket.socket(family, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((addr_str, port))
                sock.listen(5)
                listen_sockets.append(sock)
                proto_str = "IPv6" if family == socket.AF_INET6 else "IPv4"
                print(f"[TCP Listener] Listening {proto_str} on {addr_str}:{port}")
            except Exception as e:
                print(f"[TCP Listener] {proto_str} bind failed on port {port}: {e}")

    while True:
        if not listen_sockets:
            time.sleep(1)
            continue

        rlist, _, _ = select.select(listen_sockets, [], [], 1)
        for s in rlist:
            try:
                conn, addr = s.accept()
                data = conn.recv(64 * 1024)
                if not data:
                    print(f"[TCP Listener] Empty data from {addr}, closing")
                    conn.close()
                    continue

                print(f"[TCP Listener] RAW recv from {addr}: {data!r}")

                try:
                    msg = json.loads(data.decode("utf-8"))
                    print(f"[TCP Listener] Decoded JSON from {addr}: {msg}")
                except Exception as e:
                    print(f"[TCP Listener] JSON decode error from {addr}: {e}")
                    conn.close()
                    continue

                if msg.get("type") == "PEER_EXCHANGE_REQUEST":
                    peer_id = msg.get("id") or f"did:hmp:{addr[0]}:{addr[1]}"
                    peer_name = msg.get("name", "unknown")
                    peer_addrs = msg.get("addresses", []) or []

                    valid_addrs = []
                    for a in peer_addrs:
                        addr_value = a.get("addr")
                        nonce = a.get("nonce")
                        pow_hash = a.get("pow_hash")
                        difficulty = a.get("difficulty")
                        dt = a.get("datetime")
                        pubkey = a.get("pubkey")

                        if not addr_value:
                            print(f"[TCP Listener] Skip addr (no addr field): {a}")
                            continue

                        addr_norm = storage.normalize_address(addr_value)
                        if not addr_norm:
                            print(f"[TCP Listener] Can't normalize {addr_value}, skip")
                            continue

                        if nonce is None or not pow_hash or not pubkey:
                            print(f"[TCP Listener] Skip addr (incomplete): {a}")
                            continue

                        ok = storage.verify_pow(peer_id, pubkey, addr_norm, nonce, pow_hash, dt, difficulty)
                        print(f"[TCP Listener] Verify PoW for {addr_norm} = {ok}")
                        if not ok:
                            continue

                        existing = storage.get_peer_address(peer_id, addr_norm)
                        try:
                            existing_dt = dateutil.parser.isoparse(existing.get("datetime")) if existing else None
                            dt_obj = dateutil.parser.isoparse(dt) if dt else None
                        except Exception as e:
                            print(f"[TCP Listener] datetime parse error for {addr_norm}: {e}")
                            continue

                        if existing_dt and dt_obj and existing_dt >= dt_obj:
                            print(f"[TCP Listener] Skip old addr {addr_norm} (dt={dt})")
                            continue

                        a_copy = dict(a)
                        a_copy["addr"] = addr_norm
                        valid_addrs.append(a_copy)

                    if valid_addrs:
                        storage.add_or_update_peer(
                            peer_id=peer_id,
                            name=peer_name,
                            addresses=valid_addrs,
                            source="incoming",
                            status="online"
                        )
                        print(f"[TCP Listener] Stored {len(valid_addrs)} addrs for peer {peer_id}")
                    else:
                        print(f"[TCP Listener] No valid addrs from {peer_id}")

                    print(f"[TCP Listener] Handshake from {peer_id} ({addr}) -> name={peer_name}")

                    # Готовим список пиров для ответа
                    is_lan = storage.is_private(addr[0])
                    peers_list = []

                    for peer in storage.get_known_peers(my_id, limit=50):
                        peer_id_local = peer["id"]
                        try:
                            addresses = json.loads(peer["addresses"])
                        except:
                            addresses = []

                        updated_addresses = []
                        for a in addresses:
                            try:
                                proto, hostport = a["addr"].split("://", 1)
                                host, port = storage.parse_hostport(hostport)
                                if not host or not port:
                                    continue

                                if not is_lan and not is_public(host):
                                    continue

                                if storage.is_ipv6(host) and host.startswith("fe80:"):
                                    scope_id = storage.get_ipv6_scope(host)
                                    if scope_id:
                                        host = f"{host}%{scope_id}"

                                updated_addresses.append({
                                    "addr": f"{proto}://{host}:{port}"
                                })
                            except Exception:
                                continue

                        peers_list.append({
                            "id": peer_id_local,
                            "addresses": updated_addresses
                        })

                    print(f"[TCP Listener] Sending {len(peers_list)} peers back to {peer_id}")
                    conn.sendall(json.dumps(peers_list).encode("utf-8"))

                conn.close()
            except Exception as e:
                print(f"[TCP Listener] Connection handling error: {e}")

# ---------------------------
# Запуск потоков
# ---------------------------
def start_sync(bootstrap_file="bootstrap.txt"):
    # 1) загрузка bootstrap
    load_bootstrap_peers(bootstrap_file)

    # 2) пересчитать локальные config-derived переменные (теперь bootstrap и config загружены)
    global local_addresses, global_addresses, all_addresses, local_ports
    local_addresses = storage.get_config_value("local_addresses", [])
    global_addresses = storage.get_config_value("global_addresses", [])
    all_addresses = local_addresses + global_addresses
    local_ports = storage.get_local_ports()
    print(f"[PeerSync] Local ports (after bootstrap): {local_ports}")
    print(f"[PeerSync] Local addresses (after bootstrap): {local_addresses}")

    # 3) добавить себя в таблицу peers (чтобы pubkey, адреса были в БД и др. части кода могли их читать)
    agent_pubkey = storage.get_config_value("agent_pubkey")
    # подготавливаем адреса в том же формате, который add_or_update_peer ожидает
    self_addrs = []
    for a in all_addresses:
        if isinstance(a, dict):
            self_addrs.append(a)
        else:
            self_addrs.append({"addr": a, "nonce": None, "pow_hash": None, "difficulty": None, "datetime": ""})

    try:
        storage.add_or_update_peer(
            peer_id=my_id,
            name=agent_name,
            addresses=self_addrs,
            source="self",
            status="online",
            pubkey=agent_pubkey,
            capabilities=None,
            heard_from=None
        )
        print(f"[PeerSync] Registered self {my_id} in agent_peers (pubkey present: {bool(agent_pubkey)})")
    except Exception as e:
        print(f"[PeerSync] Failed to register self in agent_peers: {e}")

    # 4) старт потоков
    threading.Thread(target=udp_discovery, daemon=True).start()
    threading.Thread(target=tcp_peer_exchange, daemon=True).start()
    threading.Thread(target=tcp_listener, daemon=True).start()
