# agents/peer_sync.py

import socket
import threading
import time
import json
import uuid
import ipaddress
import re
from tools.storage import Storage
from datetime import datetime
import select

storage = Storage()
my_id = storage.get_config_value("agent_id", str(uuid.uuid4()))
agent_name = storage.get_config_value("agent_name", "HMP-Agent")

# ======================
# Парсер host:port
# ======================
def parse_hostport(hostport):
    if hostport.startswith("["):  # IPv6
        match = re.match(r"\[(.+)\]:(\d+)", hostport)
        if match:
            host = match.group(1)
            port = int(match.group(2))
            return host, port
    else:  # IPv4
        if ":" in hostport:
            host, port = hostport.rsplit(":", 1)
            return host, int(port)
    return None, None

# ======================
# Сбор TCP/UDP портов для прослушивания
# ======================
def get_listening_ports():
    tcp_ports = set()
    udp_ports = set()
    for key in ["global_addresses", "local_addresses"]:
        addresses = storage.get_config_value(key, [])
        for a in addresses:
            try:
                proto, hostport = a.split("://", 1)
                host, port = parse_hostport(hostport)
                if host is None or port is None:
                    continue
                if proto == "tcp":
                    tcp_ports.add((host, port))
                elif proto in ["udp", "utp"]:
                    udp_ports.add((host, port))
                elif proto == "any":
                    tcp_ports.add((host, port))
                    udp_ports.add((host, port))
            except Exception as e:
                print(f"[PeerSync] Ошибка разбора адреса {a}: {e}")
                continue
    return sorted(tcp_ports), sorted(udp_ports)

tcp_ports, udp_ports = get_listening_ports()

# ======================
# LAN Discovery (только local_addresses)
# ======================
def lan_discovery():
    DISCOVERY_INTERVAL = 300
    local_addresses = storage.get_config_value("local_addresses", [])
    udp_port_set = set()
    for a in local_addresses:
        _, port = parse_hostport(a.split("://", 1)[1])
        if port:
            udp_port_set.add(port)

    while True:
        local_ip = get_local_ip()
        if not local_ip:
            time.sleep(DISCOVERY_INTERVAL)
            continue

        net = ipaddress.ip_network(local_ip + '/24', strict=False)
        for ip in net.hosts():
            if str(ip) == local_ip:
                continue
            for port in udp_port_set:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(0.5)
                    msg = json.dumps({
                        "id": my_id,
                        "name": agent_name,
                        "addresses": local_addresses
                    }).encode("utf-8")
                    sock.sendto(msg, (str(ip), port))
                    sock.close()
                except:
                    continue
        time.sleep(DISCOVERY_INTERVAL)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None

# ======================
# UDP Discovery Listener
# ======================
def udp_discovery_listener():
    sockets = []
    for _, port in udp_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", port))
        sockets.append(sock)

    while True:
        for sock in sockets:
            try:
                data, addr = sock.recvfrom(2048)
                msg = json.loads(data.decode("utf-8"))
                peer_id = msg.get("id")
                if peer_id == my_id:
                    continue

                name = msg.get("name", "unknown")
                addresses = msg.get("addresses", [f"{addr[0]}:{sock.getsockname()[1]}"])
                normalized_addresses = []
                for a in addresses:
                    norm = storage.normalize_address(a)
                    if norm is None:
                        continue
                    proto, _ = norm.split("://")
                    if proto in ["udp", "any"]:
                        normalized_addresses.append(norm)

                if normalized_addresses:
                    storage.add_or_update_peer(peer_id, name, normalized_addresses, "discovery", "online")
            except:
                continue

# ======================
# UDP Discovery Sender (только global_addresses)
# ======================
def udp_discovery_sender():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    global_addresses = storage.get_config_value("global_addresses", [])
    msg = {"id": my_id, "name": agent_name, "addresses": global_addresses}

    udp_port_set = set()
    for a in global_addresses:
        _, port = parse_hostport(a.split("://", 1)[1])
        if port:
            udp_port_set.add(port)

    last_broadcast = 0
    DISCOVERY_INTERVAL = 60
    BROADCAST_INTERVAL = 600

    while True:
        now = time.time()
        if int(now) % DISCOVERY_INTERVAL == 0:
            for port in udp_port_set:
                sock.sendto(json.dumps(msg).encode("utf-8"), ("239.255.0.1", port))
        if now - last_broadcast > BROADCAST_INTERVAL:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            for port in udp_port_set:
                sock.sendto(json.dumps(msg).encode("utf-8"), ("255.255.255.255", port))
            last_broadcast = now
        time.sleep(1)

# ======================
# TCP Listener (для Peer Exchange)
# ======================
def tcp_listener():
    sockets = []
    for host, port in tcp_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            bind_host = "" if host in ["0.0.0.0", "any"] else host
            sock.bind((bind_host, port))
            sock.listen(5)
            sockets.append(sock)
            print(f"[TCP Listener] Слушаем на {bind_host}:{port}")
        except Exception as e:
            print(f"[TCP Listener] Ошибка bind/listen {host}:{port} -> {e}")

    while True:
        if not sockets:
            time.sleep(1)
            continue
        readable, _, _ = select.select(sockets, [], [], 1)
        for s in readable:
            try:
                conn, addr = s.accept()
                data = conn.recv(1024)
                if data == b"PEER_EXCHANGE_REQUEST":
                    print(f"[TCP Listener] Получен PEER_EXCHANGE_REQUEST от {addr}")
                conn.close()
            except:
                continue

# ======================
# Peer Exchange (TCP)
# ======================
def peer_exchange():
    PEER_EXCHANGE_INTERVAL = 120
    while True:
        peers = storage.get_online_peers(limit=50)
        for peer in peers:
            peer_id, addresses = peer["id"], peer["addresses"]
            if peer_id == my_id:
                continue

            try:
                addr_list = json.loads(addresses)
                for addr in addr_list:
                    norm = storage.normalize_address(addr)
                    if norm is None:
                        continue
                    proto, hostport = norm.split("://")
                    if proto not in ["tcp", "any"]:
                        continue

                    try:
                        host, port = parse_hostport(hostport)
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(2)
                        s.connect((host, port))
                        s.sendall(b"PEER_EXCHANGE_REQUEST")
                        s.close()
                        break
                    except:
                        continue
            except:
                continue
        time.sleep(PEER_EXCHANGE_INTERVAL)

# ======================
# Основной запуск
# ======================
def start_sync():
    print("[PeerSync] Запуск фоновой синхронизации")
    storage.load_bootstrap()
    threading.Thread(target=udp_discovery_listener, daemon=True).start()
    threading.Thread(target=udp_discovery_sender, daemon=True).start()
    threading.Thread(target=peer_exchange, daemon=True).start()
    threading.Thread(target=lan_discovery, daemon=True).start()
    threading.Thread(target=tcp_listener, daemon=True).start()

    while True:
        time.sleep(60)