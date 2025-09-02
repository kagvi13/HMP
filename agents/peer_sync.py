# agent/peer_sync.py

import socket
import json
import time
import threading
import select
import netifaces
import ipaddress

from datetime import datetime, timezone
from tools.storage import Storage

UTC = timezone.utc

storage = Storage()

# ---------------------------
# Конфигурация
# ---------------------------
my_id = storage.get_config_value("agent_id")
my_pubkey = storage.get_config_value("pubkey")
agent_name = storage.get_config_value("agent_name", "unknown")

local_addresses = storage.get_addresses("local")
global_addresses = storage.get_addresses("global")
all_addresses = local_addresses + global_addresses # один раз

#local_ports = list(set(storage.get_local_ports()))
#print(f"[PeerSync] Local ports: {local_ports}")

#print(f"[INFO] ID: {my_id}, NAME: {agent_name}: ADDRESS: {local_addresses} + {global_addresses} = {all_addresses}; Local ports: {local_ports}")

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
            heard_from=None,
            strict=False
        )

        print(f"[Bootstrap] Loaded peer {did} -> {expanded_addresses}")

# ---------------------------
# start_peer_services
# ---------------------------
def start_peer_services(port):
    """Запускаем UDP и TCP слушатели на всех интерфейсах сразу"""

    # UDP (один сокет для IPv4 и IPv6)
    udp_sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)  # слушаем и IPv4, и IPv6
    udp_sock.bind(("::", port))
    print(f"[UDP Discovery] Listening on [::]:{port} (IPv4+IPv6)")

    # TCP (один сокет для IPv4 и IPv6)
    tcp_sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)  # слушаем и IPv4, и IPv6
    tcp_sock.bind(("::", port))
    tcp_sock.listen()
    print(f"[TCP Listener] Listening on [::]:{port} (IPv4+IPv6)")

    return udp_sock, tcp_sock

# ---------------------------
# UDP Discovery
# ---------------------------
def udp_discovery(sock, local_ports):
    """Приём и рассылка discovery через один сокет (IPv4+IPv6)."""
    DISCOVERY_INTERVAL = 30
    MAX_PACKET_SIZE = 1200  # безопасный лимит под UDP
    chunks_buffer = {}  # addr -> {chunk_idx: data, total: n}

    def send_discovery_packets(msg_dict, dest, port):
        """Разбивка JSON на чанки и отправка по UDP."""
        msg_json = json.dumps(msg_dict)
        chunks = [msg_json[i:i + MAX_PACKET_SIZE] for i in range(0, len(msg_json), MAX_PACKET_SIZE)]
        total = len(chunks)
        for idx, chunk in enumerate(chunks):
            pkt = json.dumps({
                "chunk": idx,
                "total": total,
                "data": chunk
            }).encode("utf-8")
            try:
                if ":" not in dest:  # IPv4
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                else:  # IPv6
                    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

                s.sendto(pkt, (dest, port))
                s.close()
            except Exception as e:
                print(f"[UDP Discovery] send error to {dest}:{port} -> {e}")

    while True:
        # --- Приём сообщений ---
        try:
            rlist, _, _ = select.select([sock], [], [], 0.5)
            for s in rlist:
                try:
                    data, addr = s.recvfrom(4096)
                    pkt = json.loads(data.decode("utf-8"))

                    if "chunk" in pkt and "total" in pkt and "data" in pkt:
                        buf = chunks_buffer.setdefault(addr, {"chunks": {}, "total": pkt["total"]})
                        buf["chunks"][pkt["chunk"]] = pkt["data"]
                        if len(buf["chunks"]) == buf["total"]:
                            full_msg_json = "".join(buf["chunks"][i] for i in sorted(buf["chunks"]))
                            msg = json.loads(full_msg_json)
                            print(f"[UDP Discovery] received full msg (with pubkey={bool(msg.get('pubkey'))}) from {addr}")
                            del chunks_buffer[addr]
                        else:
                            continue
                    else:
                        msg = pkt  # старый формат
                        print(f"[UDP Discovery] received short msg (with pubkey={bool(msg.get('pubkey'))}) from {addr}")

                    peer_id = msg.get("id")
                    if peer_id == my_id:
                        continue
                    name = msg.get("name", "unknown")
                    raw_addresses = msg.get("addresses", [])
                    pubkey = msg.get("pubkey")

                    addresses = []
                    for a in raw_addresses:
                        if isinstance(a, dict) and "addr" in a:
                            addresses.append({
                                "addr": storage.normalize_address(a["addr"]),
                                "nonce": a.get("nonce"),
                                "pow_hash": a.get("pow_hash"),
                                "datetime": a.get("datetime")
                            })
                        elif isinstance(a, str):
                            addresses.append({
                                "addr": storage.normalize_address(a),
                                "nonce": None,
                                "pow_hash": None,
                                "datetime": datetime.now(timezone.utc).replace(microsecond=0).isoformat()
                            })

                    storage.add_or_update_peer(
                        peer_id, name, addresses,
                        source="discovery", status="online",
                        pubkey=pubkey, strict=False
                    )
                    print(f"[UDP Discovery] peer={peer_id} from {addr} (pubkey={bool(pubkey)})")
                except Exception as e:
                    print(f"[UDP Discovery] receive error: {e}")
        except Exception as e:
            print(f"[UDP Discovery] select() error: {e}")

        # --- Вывод интерфейсов и их адресов ---
        print("[UDP Discovery] Interfaces:")
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            ipv4_list = addrs.get(netifaces.AF_INET, [])
            ipv6_list = addrs.get(netifaces.AF_INET6, [])
            try:
                if_idx = socket.if_nametoindex(iface)
            except Exception:
                if_idx = None
            print(f"  {iface} (idx={if_idx}) - IPv4: {ipv4_list}, IPv6: {ipv6_list}")

        # --- Формируем локальные адреса для рассылки ---
        local_addresses = []
        for iface in netifaces.interfaces():
            for a in netifaces.ifaddresses(iface).get(netifaces.AF_INET, []):
                ip = a.get("addr")
                if ip:
                    local_addresses.append({
                        "addr": storage.normalize_address(f"any://{ip}:{local_ports[0]}"),
                        "nonce": 0,
                        "pow_hash": "0"*64,
                        "datetime": datetime.now(timezone.utc).replace(microsecond=0).isoformat()
                    })

        # --- Вывод известных хостов ---
        peers = storage.get_known_peers(my_id)
        print("[UDP Discovery] Known peers:", [p["id"] for p in peers])

        msg_dict = {
            "id": my_id,
            "name": agent_name,
            "addresses": local_addresses,
            "pubkey": my_pubkey
        }
        print(f"[UDP Discovery] sending msg (with pubkey={bool(my_pubkey)}): {msg_dict}")

        for port in local_ports:
            # IPv4 broadcast
            for iface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET, [])
                for a in addrs:
                    if "broadcast" in a:
                        send_discovery_packets(msg_dict, a["broadcast"], port)
                        send_discovery_packets(msg_dict, "255.255.255.255", port)

            # IPv6 multicast пока выключен для отладки
            # for iface in netifaces.interfaces():
            #     ifaddrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET6, [])
            #     for a in ifaddrs:
            #         ip = a.get("addr")
            #         if not ip:
            #             continue
            #         multicast_addr = "ff02::1"
            #         try:
            #             if ip.startswith("fe80:"):
            #                 if_idx = socket.if_nametoindex(iface)
            #                 multicast_addr = f"ff02::1%{if_idx}"
            #         except Exception as e:
            #             print(f"[UDP Discovery] IPv6 multicast addr build error on {iface}: {e}")
            #             multicast_addr = "ff02::1"
            #         send_discovery_packets(msg_dict, multicast_addr, port)

        time.sleep(DISCOVERY_INTERVAL)

# ---------------------------
# TCP Peer Exchange (исходящие)
# ---------------------------
def tcp_peer_exchange():
    PEER_EXCHANGE_INTERVAL = 20
    while True:
        peers = storage.get_known_peers(my_id, limit=50)
        print(f"[PeerExchange] Checking {len(peers)} peers (raw DB)...")

        for peer in peers:
            # sqlite3.Row → dict
            if not isinstance(peer, dict):
                peer = dict(peer)

            peer_id = peer.get("id")
            if peer_id == my_id:
                continue

            try:
                addr_list = json.loads(peer.get("addresses", "[]"))
            except Exception as e:
                print(f"[PeerExchange] JSON decode error for peer {peer_id}: {e}")
                addr_list = []

            for addr in addr_list:
                norm = storage.normalize_address(addr)
                if not norm:
                    continue
                proto, hostport = norm.split("://", 1)
                if proto not in ["tcp", "any"]:
                    continue
                host, port = storage.parse_hostport(hostport)
                if not host or not port:
                    continue

                print(f"[PeerExchange] Trying {peer_id} at {host}:{port} (proto={proto})")
                try:
                    sock = socket.socket(
                        socket.AF_INET6 if storage.is_ipv6(host) else socket.AF_INET,
                        socket.SOCK_STREAM
                    )
                    sock.settimeout(3)
                    sock.connect((host, port))

                    # LAN или Интернет
                    if storage.is_private(host):
                        send_addresses = all_addresses
                    else:
                        send_addresses = [
                            a for a in all_addresses
                            if not storage.is_private(storage.parse_hostport(a.split("://", 1)[1])[0])
                        ]

                    handshake = {
                        "type": "PEER_EXCHANGE_REQUEST",
                        "id": my_id,
                        "name": agent_name,
                        "addresses": send_addresses,
                    }
                    sock.sendall(json.dumps(handshake).encode("utf-8"))

                    data = sock.recv(64 * 1024)
                    sock.close()

                    if not data:
                        print(f"[PeerExchange] No data from {host}:{port}")
                        continue

                    try:
                        peers_recv = json.loads(data.decode("utf-8"))
                        for p in peers_recv:
                            if p.get("id") and p["id"] != my_id:
                                storage.add_or_update_peer(
                                    p["id"],
                                    p.get("name", "unknown"),
                                    p.get("addresses", []),
                                    "peer_exchange",
                                    "online",
                                    strict=False
                                )
                        print(f"[PeerExchange] Received {len(peers_recv)} peers from {host}:{port}")
                    except Exception as e:
                        print(f"[PeerExchange] Decode error from {host}:{port} -> {e}")
                        continue

                    break
                except Exception as e:
                    print(f"[PeerExchange] Connection to {host}:{port} failed: {e}")
                    continue

        time.sleep(PEER_EXCHANGE_INTERVAL)

# ---------------------------
# TCP Listener (входящие)
# ---------------------------
def tcp_listener(sock):
    """Слушатель TCP (один сокет на IPv6, работает и для IPv4)."""
    while True:
        try:
            rlist, _, _ = select.select([sock], [], [], 1)
            for s in rlist:
                try:
                    conn, addr = s.accept()
                    data = conn.recv(64 * 1024)
                    if not data:
                        conn.close()
                        continue

                    try:
                        msg = json.loads(data.decode("utf-8"))
                    except Exception as e:
                        print(f"[TCP Listener] JSON decode error from {addr}: {e}")
                        conn.close()
                        continue

                    if msg.get("type") == "PEER_EXCHANGE_REQUEST":
                        peer_id = msg.get("id") or f"did:hmp:{addr[0]}:{addr[1]}"
                        peer_name = msg.get("name", "unknown")
                        raw_addrs = msg.get("addresses", [])
                        pubkey = msg.get("pubkey")

                        # Нормализация и подготовка адресов
                        addresses = []
                        for a in raw_addrs:
                            if isinstance(a, dict) and "addr" in a:
                                addresses.append({
                                    "addr": storage.normalize_address(a["addr"]),
                                    "nonce": a.get("nonce"),
                                    "pow_hash": a.get("pow_hash"),
                                    "datetime": a.get("datetime")
                                })
                            elif isinstance(a, str):
                                addresses.append({
                                    "addr": storage.normalize_address(a),
                                    "nonce": None,
                                    "pow_hash": None,
                                    "datetime": datetime.now(UTC).replace(microsecond=0).isoformat()
                                })

                        storage.add_or_update_peer(
                            peer_id, peer_name, addresses,
                            source="incoming", status="online",
                            pubkey=pubkey, strict=False
                        )
                        print(f"[TCP Listener] Handshake from {peer_id} ({addr})")

                        # LAN или Интернет
                        is_lan = storage.is_private(addr[0])

                        # Формируем список пиров для отправки
                        peers_list = []
                        for peer in storage.get_known_peers(my_id, limit=50):
                            pid = peer["id"]
                            try:
                                peer_addrs = json.loads(peer.get("addresses", "[]"))
                            except:
                                peer_addrs = []

                            updated_addresses = []
                            for a in peer_addrs:
                                # Нормализация и проверка
                                addr_norm = storage.normalize_address(a.get("addr") if isinstance(a, dict) else a)
                                if not addr_norm:
                                    continue
                                proto, hostport = addr_norm.split("://", 1)
                                host, port = storage.parse_hostport(hostport)

                                # Фильтруем приватные адреса при обмене с внешними пирами
                                if not is_lan and storage.is_private(host):
                                    continue

                                updated_addresses.append({
                                    "addr": f"{proto}://{host}:{port}",
                                    "nonce": a.get("nonce") if isinstance(a, dict) else None,
                                    "pow_hash": a.get("pow_hash") if isinstance(a, dict) else None,
                                    "datetime": a.get("datetime") if isinstance(a, dict) else None
                                })

                            peers_list.append({
                                "id": pid,
                                "addresses": updated_addresses,
                                "pubkey": peer.get("pubkey")
                            })

                        conn.sendall(json.dumps(peers_list).encode("utf-8"))

                    conn.close()
                except Exception as e:
                    print(f"[TCP Listener] Connection handling error: {e}")
        except Exception as e:
            print(f"[TCP Listener] select() error: {e}")

# ---------------------------
# Запуск потоков
# ---------------------------
def start_sync(bootstrap_file="bootstrap.txt"):
    load_bootstrap_peers(bootstrap_file)

    local_ports = list(set(storage.get_local_ports()))
    print(f"[PeerSync] Local ports: {local_ports}")

    for port in local_ports:
        udp_sock, tcp_sock = start_peer_services(port)

        threading.Thread(target=udp_discovery, args=(udp_sock, local_ports), daemon=True).start()
        threading.Thread(target=tcp_listener, args=(tcp_sock,), daemon=True).start()

    threading.Thread(target=tcp_peer_exchange, daemon=True).start()