# agent/peer_sync.py

import socket
import json
import time
import threading
import select
import netifaces
import re
import ipaddress

from datetime import datetime, timezone as UTC
from tools.storage import Storage

storage = Storage()

# ---------------------------
# Конфигурация
# ---------------------------
my_id = storage.get_config_value("agent_id")
agent_name = storage.get_config_value("agent_name", "unknown")
local_addresses = storage.get_config_value("local_addresses", [])
global_addresses = storage.get_config_value("global_addresses", [])
all_addresses = local_addresses + global_addresses  # один раз

local_ports = storage.get_local_ports()
print(f"[PeerSync] Local ports: {local_ports}")

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

        # Расширяем any:// в tcp/udp и приводим к новому формату
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
                            "expires": addr.get("expires", "")
                        })
                # уже новый формат → оставляем как есть
                elif "addr" in addr:
                    expanded_addresses.append(addr)

            elif isinstance(addr, str):
                if addr.startswith("any://"):
                    hostport = addr[len("any://"):]
                    expanded_addresses.extend([
                        {"addr": f"tcp://{hostport}", "nonce": None, "pow_hash": None, "difficulty": None, "expires": ""},
                        {"addr": f"udp://{hostport}", "nonce": None, "pow_hash": None, "difficulty": None, "expires": ""}
                    ])
                else:
                    expanded_addresses.append({
                        "addr": addr,
                        "nonce": None,
                        "pow_hash": None,
                        "difficulty": None,
                        "expires": ""
                    })

        # Сохраняем в storage
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
    DISCOVERY_INTERVAL = 30
    local_addresses = storage.get_config_value("local_addresses", [])
    msg_data = json.dumps({
        "id": my_id,
        "name": agent_name,
        "addresses": local_addresses
    }).encode("utf-8")

    # Создаём UDP сокеты для прослушки
    listen_sockets = []
    for port in local_ports:
        # IPv4
        try:
            sock4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock4.bind(("", port))
            listen_sockets.append(sock4)
            print(f"[UDP Discovery] Listening IPv4 on *:{port}")
        except Exception as e:
            print(f"[UDP Discovery] IPv4 bind failed on port {port}: {e}")

        # IPv6
        try:
            sock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            sock6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock6.bind(("::", port))
            listen_sockets.append(sock6)
            print(f"[UDP Discovery] Listening IPv6 on [::]:{port}")
        except Exception as e:
            print(f"[UDP Discovery] IPv6 bind failed on port {port}: {e}")

    while True:
        # Приём сообщений
        rlist, _, _ = select.select(listen_sockets, [], [], 0.5)
        for sock in rlist:
            try:
                data, addr = sock.recvfrom(2048)
                msg = json.loads(data.decode("utf-8"))
                peer_id = msg.get("id")
                if peer_id == my_id:
                    continue
                name = msg.get("name", "unknown")
                addresses = msg.get("addresses", [])
                storage.add_or_update_peer(peer_id, name, addresses, "discovery", "online")
                print(f"[UDP Discovery] peer={peer_id} from {addr}")
            except Exception as e:
                print(f"[UDP Discovery] receive error: {e}")

        # Отправка broadcast/multicast
        for port in local_ports:
            # IPv4 broadcast
            for iface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET, [])
                for a in addrs:
                    if "broadcast" in a:
                        try:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                            sock.sendto(msg_data, (a["broadcast"], port))
                            sock.close()
                        except Exception:
                            continue
            # IPv6 multicast ff02::1
            for iface in netifaces.interfaces():
                ifaddrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET6, [])
                for a in ifaddrs:
                    addr = a.get("addr")
                    if not addr:
                        continue
                    multicast_addr = f"ff02::1%{iface}" if addr.startswith("fe80:") else "ff02::1"
                    try:
                        sock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                        sock6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_IF, socket.if_nametoindex(iface))
                        sock6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, 1)
                        sock6.sendto(msg_data, (multicast_addr, port))
                        sock6.close()
                    except Exception:
                        continue

        time.sleep(DISCOVERY_INTERVAL)

# ---------------------------
# TCP Peer Exchange (исходящие)
# ---------------------------
def tcp_peer_exchange():
    PEER_EXCHANGE_INTERVAL = 20  # для отладки
    while True:
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

                    # LAN или Интернет
                    if storage.is_private(host):
                        send_addresses = all_addresses
                    else:
                        send_addresses = [a for a in all_addresses
                                          if is_public(stprage.parse_hostport(a.split("://", 1)[1])[0])]

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
                                    p["id"], p.get("name", "unknown"), p.get("addresses", []),
                                    "peer_exchange", "online"
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
def tcp_listener():
    listen_sockets = []
    for port in local_ports:
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
                    peer_addrs = msg.get("addresses", [])

                    storage.add_or_update_peer(peer_id, peer_name, peer_addrs,
                                               source="incoming", status="online")
                    print(f"[TCP Listener] Handshake from {peer_id} ({addr})")

                    # LAN или Интернет
                    is_lan = storage.is_private(addr[0])

                    peers_list = []
                    for peer in storage.get_known_peers(my_id, limit=50):
                        peer_id = peer["id"]
                        try:
                            addresses = json.loads(peer["addresses"])
                        except:
                            addresses = []

                        updated_addresses = []
                        for a in addresses:
                            proto, hostport = a.split("://")
                            host, port = storage.parse_hostport(hostport)

                            # Фильтруем по LAN/Internet
                            if not is_lan and not is_public(host):
                                continue

                            # IPv6 link-local
                            if storage.is_ipv6(host) and host.startswith("fe80:"):
                                scope_id = storage.get_ipv6_scope(host)
                                if scope_id:
                                    host = f"{host}%{scope_id}"

                            updated_addresses.append(f"{proto}://{host}:{port}")

                        peers_list.append({"id": peer_id, "addresses": updated_addresses})

                    conn.sendall(json.dumps(peers_list).encode("utf-8"))

                conn.close()
            except Exception as e:
                print(f"[TCP Listener] Connection handling error: {e}")

# ---------------------------
# Запуск потоков
# ---------------------------
def start_sync(bootstrap_file="bootstrap.txt"):
    load_bootstrap_peers(bootstrap_file)
    print(f"[PeerSync] Local ports: {local_ports}")

    threading.Thread(target=udp_discovery, daemon=True).start()
    threading.Thread(target=tcp_peer_exchange, daemon=True).start()
    threading.Thread(target=tcp_listener, daemon=True).start()