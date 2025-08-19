# agents/peer_sync.py

import socket
import threading
import time
import json
import uuid
import ipaddress
from tools.storage import Storage

storage = Storage()
my_id = storage.get_config_value("agent_id", "")

# ======================
# LAN Discovery
# ======================
def lan_discovery(udp_port: int):
    """
    Периодический поиск локальных агентов в сети.
    """
    DISCOVERY_INTERVAL = 300  # каждые 5 минут

    while True:
        local_ip = get_local_ip()
        if not local_ip:
            time.sleep(DISCOVERY_INTERVAL)
            continue

        net = ipaddress.ip_network(local_ip + '/24', strict=False)  # /24 по умолчанию
        for ip in net.hosts():
            if str(ip) == local_ip:
                continue  # пропускаем себя
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(0.5)
                msg = json.dumps({"ping": "HMP"}).encode("utf-8")
                sock.sendto(msg, (str(ip), udp_port))
                sock.close()
            except:
                continue

        time.sleep(DISCOVERY_INTERVAL)

def get_local_ip():
    """Возвращает локальный IP хоста."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None

# ======================
# UDP Discovery
# ======================
def udp_discovery_listener(udp_port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", udp_port))
    while True:
        data, addr = sock.recvfrom(1024)
        try:
            msg = json.loads(data.decode("utf-8"))
            peer_id = msg.get("id")
            name = msg.get("name", "unknown")
            addresses = msg.get("addresses", [f"{addr[0]}:{msg.get('tcp_port', udp_port)}"])
            normalized_addresses = []
            for a in addresses:
                norm = storage.normalize_address(a)
                if norm is None:
                    continue
                proto, hostport = norm.split("://")
                if proto in ["udp", "any"]:
                    normalized_addresses.append(norm)
            if normalized_addresses:
                storage.add_or_update_peer(peer_id, name, normalized_addresses, "discovery", "online")
        except Exception as e:
            print("[PeerSync] Ошибка при обработке UDP пакета:", e)

def udp_discovery_sender(agent_id: str, agent_name: str, udp_port: int, tcp_port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    msg = {"id": agent_id, "name": agent_name, "tcp_port": tcp_port, "addresses": [f"127.0.0.1:{tcp_port}"]}
    last_broadcast = 0
    DISCOVERY_INTERVAL = 60
    BROADCAST_INTERVAL = 600
    while True:
        now = time.time()
        if int(now) % DISCOVERY_INTERVAL == 0:
            sock.sendto(json.dumps(msg).encode("utf-8"), ("239.255.0.1", udp_port))
        if now - last_broadcast > BROADCAST_INTERVAL:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(json.dumps(msg).encode("utf-8"), ("255.255.255.255", udp_port))
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
                continue  # пропускаем собственный агент

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
                        print(f"[PeerSync] Успешно подключились к {peer_id} ({norm})")
                        break
                    except Exception as e:
                        print(f"[PeerSync] Не удалось подключиться к {peer_id} ({norm}): {e}")
            except Exception as e:
                print(f"[PeerSync] Ошибка обработки адресов {peer_id} ({addresses}): {e}")
        time.sleep(PEER_EXCHANGE_INTERVAL)

# ======================
# Основной запуск
# ======================
def start_sync():
    print("[PeerSync] Запуск фоновой синхронизации")
    udp_port = int(storage.get_config_value("udp_port", 4000))
    tcp_port = int(storage.get_config_value("tcp_port", 5000))
    agent_id = storage.get_config_value("agent_id", str(uuid.uuid4()))
    agent_name = storage.get_config_value("agent_name", "HMP-Agent")

    storage.load_bootstrap()

    threading.Thread(target=udp_discovery_listener, args=(udp_port,), daemon=True).start()
    threading.Thread(target=udp_discovery_sender, args=(agent_id, agent_name, udp_port, tcp_port), daemon=True).start()
    threading.Thread(target=peer_exchange, daemon=True).start()
    threading.Thread(target=lan_discovery, args=(udp_port,), daemon=True).start()  # новый поток

    while True:
        time.sleep(60)
