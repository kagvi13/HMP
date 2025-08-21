# agent/peer_sync.py

import socket
import json
import time
import threading
import select
import netifaces
import re

from datetime import datetime, timezone as UTC
from tools.storage import Storage

storage = Storage()

# ---------------------------
# Вспомогательные функции
# ---------------------------
def parse_hostport(s: str):
    """
    Разбирает "IP:port" или "[IPv6]:port" и возвращает (host, port)
    """
    s = s.strip()
    if s.startswith("["):
        # IPv6 с портом: [addr]:port
        host, _, port = s[1:].partition("]:")
        try:
            port = int(port)
        except:
            port = None
        return host, port
    else:
        # IPv4 или IPv6 без []
        if ":" in s:
            host, port = s.rsplit(":", 1)
            try:
                port = int(port)
            except:
                port = None
            return host, port
        return s, None

def is_ipv6(host: str):
    try:
        socket.inet_pton(socket.AF_INET6, host)
        return True
    except OSError:
        return False

# ---------------------------
# Конфигурация
# ---------------------------
my_id = storage.get_config_value("agent_id")
agent_name = storage.get_config_value("agent_name", "unknown")
local_addresses = storage.get_config_value("local_addresses", [])

# Получаем уникальные локальные порты для прослушки TCP/UDP
def get_local_ports():
    ports = set()
    for addr in local_addresses:
        _, port = parse_hostport(addr.split("://", 1)[1])
        if port:
            ports.add(port)
    return sorted(ports)

local_ports = get_local_ports()
print(f"[PeerSync] Local ports: {local_ports}")

# ---------------------------
# Загрузка bootstrap
# ---------------------------

def load_bootstrap_peers(filename="bootstrap.txt"):
    """
    Читает bootstrap.txt и добавляет узлы в storage.
    Формат строки: did [JSON-список адресов]
    """
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

        match = re.match(r"^(did:hmp:[\w-]+)\s+(.+)$", line)
        if not match:
            print(f"[Bootstrap] Invalid line format: {line}")
            continue

        did, addresses_json = match.groups()
        try:
            addresses = json.loads(addresses_json)
        except Exception as e:
            print(f"[Bootstrap] Invalid JSON addresses for {did}: {e}")
            continue

        # Разворачиваем any:// в tcp:// и udp://
        expanded_addresses = []
        for addr in addresses:
            if addr.startswith("any://"):
                hostport = addr[len("any://"):]
                expanded_addresses.append(f"tcp://{hostport}")
                expanded_addresses.append(f"udp://{hostport}")
            else:
                expanded_addresses.append(addr)

        storage.add_or_update_peer(did, name=None, addresses=expanded_addresses,
                                   source="bootstrap", status="offline")
        print(f"[Bootstrap] Loaded peer {did} -> {expanded_addresses}")

# ---------------------------
# TCP Listener (обработка входящих PEER_EXCHANGE_REQUEST)
# ---------------------------
def tcp_listener():
    listen_sockets = []

    # Создаём TCP сокеты на всех локальных портах
    for port in local_ports:
        try:
            sock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock4.bind(("", port))
            sock4.listen(5)
            listen_sockets.append(sock4)
            print(f"[TCP Listener] Listening IPv4 on *:{port}")
        except Exception as e:
            print(f"[TCP Listener] IPv4 bind failed on port {port}: {e}")

        try:
            sock6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock6.bind(("::", port))
            sock6.listen(5)
            listen_sockets.append(sock6)
            print(f"[TCP Listener] Listening IPv6 on [::]:{port}")
        except Exception as e:
            print(f"[TCP Listener] IPv6 bind failed on port {port}: {e}")

    while True:
        if not listen_sockets:
            time.sleep(1)
            continue
        rlist, _, _ = select.select(listen_sockets, [], [], 1)
        for s in rlist:
            try:
                conn, addr = s.accept()
                data = conn.recv(1024)

                if data == b"PEER_EXCHANGE_REQUEST":
                    print(f"[TCP Listener] PEER_EXCHANGE_REQUEST from {addr}")

                    # --- (1) Сохраняем нового пира ---
                    peer_host, peer_port = addr[0], addr[1]
                    peer_id = f"did:hmp:{peer_host}:{peer_port}"  # временный ID, пока пир не представился
                    storage.add_or_update_peer(
                        peer_id,
                        name="incoming",
                        addresses=[f"tcp4://{peer_host}:{peer_port}"],
                        source="incoming",
                        status="online"
                    )

                    # --- (2) Отправляем список известных ---
                    peers_list = []
                    for peer in storage.get_known_peers(my_id, limit=50):
                        peer_id = peer["id"]
                        addresses_json = peer["addresses"]
                        try:
                            addresses = json.loads(addresses_json)
                        except:
                            addresses = []
                        peers_list.append({"id": peer_id, "addresses": addresses})
                    payload = json.dumps(peers_list).encode("utf-8")
                    conn.sendall(payload)

                    # --- (3) Делаем встречный запрос ---
                    try:
                        with socket.create_connection((peer_host, peer_port), timeout=3) as s2:
                            s2.sendall(b"PEER_EXCHANGE_REQUEST")
                            resp = s2.recv(65536)
                            if resp:
                                new_peers = json.loads(resp.decode("utf-8"))
                                for p in new_peers:
                                    storage.add_or_update_peer(
                                        p["id"],
                                        name="from_incoming",
                                        addresses=p.get("addresses", []),
                                        source="reverse-sync",
                                        status="online"
                                    )
                                print(f"[TCP Listener] Reverse sync: got {len(new_peers)} peers from {peer_host}:{peer_port}")
                    except Exception as e:
                        print(f"[TCP Listener] Reverse sync failed with {peer_host}:{peer_port}: {e}")

                conn.close()
            except Exception as e:
                print(f"[TCP Listener] Connection handling error: {e}")

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
# TCP Peer Exchange
# ---------------------------
def tcp_peer_exchange():
    PEER_EXCHANGE_INTERVAL = 20  # для отладки сделаем меньше
    while True:
        peers = storage.get_known_peers(my_id, limit=50)
        print(f"[PeerExchange] Checking {len(peers)} peers (raw DB)...")

        for peer in peers:
            if isinstance(peer, dict):
                peer_id, addresses_json = peer["id"], peer["addresses"]
            else:
                peer_id, addresses_json = peer[0], peer[1]

            if peer_id == my_id:
                continue

            try:
                addr_list = json.loads(addresses_json)
            except Exception as e:
                print(f"[PeerExchange] JSON decode error for peer {peer_id}: {e}")
                addr_list = []

            print(f"[PeerExchange] Peer {peer_id} -> addresses={addr_list}")

            for addr in addr_list:
                norm = storage.normalize_address(addr)
                if not norm:
                    continue

                proto, hostport = norm.split("://", 1)
                if proto not in ["tcp", "any"]:
                    continue

                host, port = parse_hostport(hostport)
                if not host or not port:
                    continue

                print(f"[PeerExchange] Trying {peer_id} at {host}:{port} (proto={proto})")

                try:
                    # IPv6 link-local
                    if is_ipv6(host) and host.startswith("fe80:"):
                        scope_id = None
                        for iface in netifaces.interfaces():
                            if iface.endswith(host):
                                scope_id = socket.if_nametoindex(iface)
                                break
                        if scope_id is not None:
                            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                            sock.settimeout(3)
                            sock.connect((host, port, 0, scope_id))
                        else:
                            print(f"[PeerExchange] Skipping {host}, no scope_id found")
                            continue
                    else:
                        sock = socket.socket(socket.AF_INET6 if is_ipv6(host) else socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(3)
                        sock.connect((host, port))

                    # 🔑 Отправляем данные о себе
                    handshake = {
                        "type": "PEER_EXCHANGE_REQUEST",
                        "id": my_id,
                        "name": agent_name,
                        "addresses": my_addresses,  # список вроде ["tcp4://192.168.0.10:4010"]
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

                    break  # успешное соединение — идём к следующему пиру
                except Exception as e:
                    print(f"[PeerExchange] Connection to {host}:{port} failed: {e}")
                    continue

        time.sleep(PEER_EXCHANGE_INTERVAL)

# ---------------------------
# TCP Listener (обработка входящих PEER_EXCHANGE_REQUEST)
# ---------------------------
def tcp_listener():
    listen_sockets = []

    # Создаём TCP сокеты на всех локальных портах
    for port in local_ports:
        # IPv4
        try:
            sock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock4.bind(("", port))
            sock4.listen(5)
            listen_sockets.append(sock4)
            print(f"[TCP Listener] Listening IPv4 on *:{port}")
        except Exception as e:
            print(f"[TCP Listener] IPv4 bind failed on port {port}: {e}")

        # IPv6
        try:
            sock6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock6.bind(("::", port))
            sock6.listen(5)
            listen_sockets.append(sock6)
            print(f"[TCP Listener] Listening IPv6 on [::]:{port}")
        except Exception as e:
            print(f"[TCP Listener] IPv6 bind failed on port {port}: {e}")

    while True:
        if not listen_sockets:
            time.sleep(1)
            continue
        rlist, _, _ = select.select(listen_sockets, [], [], 1)
        for s in rlist:
            try:
                conn, addr = s.accept()
                data = conn.recv(1024)

                if not data:
                    conn.close()
                    continue

                try:
                    msg = json.loads(data.decode("utf-8"))
                except Exception:
                    conn.close()
                    continue

                if msg.get("type") == "PEER_EXCHANGE_REQUEST":
                    peer_id = msg.get("id") or f"did:hmp:{addr[0]}:{addr[1]}"
                    peer_name = msg.get("name", "unknown")
                    peer_addrs = msg.get("addresses", [])

                    # Сохраняем нового пира
                    storage.add_or_update_peer(
                        peer_id,
                        peer_name,
                        peer_addrs,
                        source="incoming",
                        status="online"
                    )
                    print(f"[TCP Listener] Handshake from {peer_id} ({addr})")

                    # Отправляем список известных пиров
                    peers_list = []
                    for peer in storage.get_known_peers(my_id, limit=50):
                        peer_id = peer["id"]
                        addresses_json = peer["addresses"]
                        try:
                            addresses = json.loads(addresses_json)
                        except:
                            addresses = []

                        # Обработка IPv6 link-local: добавить scope_id
                        updated_addresses = []
                        for a in addresses:
                            proto, hostport = a.split("://")
                            host, port = parse_hostport(hostport)
                            if is_ipv6(host) and host.startswith("fe80:"):
                                scope_id = None
                                for iface in netifaces.interfaces():
                                    iface_addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET6, [])
                                    for addr_info in iface_addrs:
                                        if addr_info.get("addr") == host:
                                            scope_id = socket.if_nametoindex(iface)
                                            break
                                    if scope_id:
                                        break
                                if scope_id:
                                    host = f"{host}%{scope_id}"
                            updated_addresses.append(f"{proto}://{host}:{port}")
                        peers_list.append({"id": peer_id, "addresses": updated_addresses})

                    payload = json.dumps(peers_list).encode("utf-8")
                    conn.sendall(payload)

                conn.close()
            except Exception as e:
                print(f"[TCP Listener] Connection handling error: {e}")

# ---------------------------
# Запуск потоков
# ---------------------------
def start_sync(bootstrap_file="bootstrap.txt"):
    # Загружаем bootstrap-пиров перед запуском discovery/peer exchange
    load_bootstrap_peers(bootstrap_file)

    # Печать локальных портов для логов
    print(f"[PeerSync] Local ports: {local_ports}")

    # Запуск потоков
    threading.Thread(target=udp_discovery, daemon=True).start()
    threading.Thread(target=tcp_peer_exchange, daemon=True).start()
    threading.Thread(target=tcp_listener, daemon=True).start()