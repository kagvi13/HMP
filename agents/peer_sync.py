# agents/peer_sync.py

import socket
import threading
import time
import json
import uuid
import ipaddress
from tools.storage import Storage
from datetime import datetime

storage = Storage()
my_id = storage.get_config_value("agent_id", str(uuid.uuid4()))
agent_name = storage.get_config_value("agent_name", "HMP-Agent")

# ======================
# Формируем TCP/UDP порты для прослушивания
# ======================
def get_listening_ports():
    tcp_ports = set()
    udp_ports = set()

    for key in ["global_addresses", "local_addresses"]:
        addresses = json.loads(storage.get_config_value(key, "[]"))
        for a in addresses:
            proto, hostport = a.split("://")
            host, port = hostport.split(":")
            port = int(port)
            if proto == "tcp":
                tcp_ports.add(port)
            elif proto in ["udp", "utp"]:
                udp_ports.add(port)
            elif proto == "any":
                tcp_ports.add(port)
                udp_ports.add(port)

    return sorted(tcp_ports), sorted(udp_ports)

tcp_ports, udp_ports = get_listening_ports()

# ======================
# LAN Discovery
# ======================
def lan_discovery():
    DISCOVERY_INTERVAL = 300  # каждые 5 минут
    udp_port_set = set(udp_ports)

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
                    msg = json.dumps({"id": my_id, "name": agent_name}).encode("utf-8")
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
    for port in udp_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", port))
        sockets.append(sock)

    while True:
        for sock in sockets:
            try:
                data, addr = sock.recvfrom(1024)
                msg = json.loads(data.decode("utf-8"))
                peer_id = msg.get("id")
                if peer_id == my_id:
                    continue  # не добавляем себя

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
# UDP Discovery Sender
# ======================
def udp_discovery_sender():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    global_addresses = json.loads(storage.get_config_value("global_addresses", "[]"))
    msg = {"id": my_id, "name": agent_name, "addresses": global_addresses}

    last_broadcast = 0
    DISCOVERY_INTERVAL = 60
    BROADCAST_INTERVAL = 600

    while True:
        now = time.time()
        if int(now) % DISCOVERY_INTERVAL == 0:
            for port in udp_ports:
                sock.sendto(json.dumps(msg).encode("utf-8"), ("239.255.0.1", port))
        if now - last_broadcast > BROADCAST_INTERVAL:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            for port in udp_ports:
                sock.sendto(json.dumps(msg).encode("utf-8"), ("255.255.255.255", port))
            last_broadcast = now
        time.sleep(1)

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
                continue  # пропускаем себя

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
                        host, port = hostport.split(":")
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(2)
                        s.connect((host, int(port)))
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

    while True:
        time.sleep(60)
