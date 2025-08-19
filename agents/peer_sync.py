# agents/peer_sync.py

"""
peer_sync.py — фоновый процесс синхронизации пиров в сети HMP
"""

import socket
import threading
import time
import json
from tools.storage import Storage

storage = Storage()

# ======================
# UDP Discovery
# ======================

def udp_discovery_listener(udp_port: int):
    """Слушаем UDP-пакеты"""
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
            storage.add_or_update_peer(peer_id, name, addresses, source="discovery", status="online")
        except Exception as e:
            print("[PeerSync] Ошибка при обработке UDP пакета:", e)


def udp_discovery_sender(agent_id: str, agent_name: str, udp_port: int, tcp_port: int):
    """Рассылаем UDP multicast/broadcast пакеты"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    msg = {
        "id": agent_id,
        "name": agent_name,
        "tcp_port": tcp_port,
        "addresses": [f"127.0.0.1:{tcp_port}"]
    }

    last_broadcast = 0
    DISCOVERY_INTERVAL = 60
    BROADCAST_INTERVAL = 600

    while True:
        now = time.time()
        # Multicast раз в минуту
        if int(now) % DISCOVERY_INTERVAL == 0:
            sock.sendto(json.dumps(msg).encode("utf-8"), ("239.255.0.1", udp_port))
        # Broadcast раз в 10 минут
        if now - last_broadcast > BROADCAST_INTERVAL:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(json.dumps(msg).encode("utf-8"), ("255.255.255.255", udp_port))
            last_broadcast = now
        time.sleep(1)


# ======================
# Peer Exchange (TCP)
# ======================

def peer_exchange():
    """Периодический обмен списками пиров"""
    PEER_EXCHANGE_INTERVAL = 120
    while True:
        peers = storage.get_online_peers(limit=50)
        for peer in peers:
            peer_id, addresses = peer["id"], peer["addresses"]
            try:
                addr = json.loads(addresses)[0]
                host, port = addr.split(":")
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((host, int(port)))
                # пока только "каркас"
                s.sendall(b"PEER_EXCHANGE_REQUEST")
                s.close()
            except Exception as e:
                print(f"[PeerSync] Не удалось подключиться к {peer_id} ({addresses}): {e}")
        time.sleep(PEER_EXCHANGE_INTERVAL)


# ======================
# Основной запуск
# ======================

def start_sync():
    print("[PeerSync] Запуск фоновой синхронизации")

    # 1. Конфиг
    udp_port = int(storage.get_config_value("udp_port", 4000))
    tcp_port = int(storage.get_config_value("tcp_port", 5000))
    agent_id = storage.get_config_value("agent_id", "unknown-agent")
    agent_name = storage.get_config_value("agent_name", "HMP-Agent")

    # 2. Bootstrap загрузка
    storage.load_bootstrap()

    # 3. UDP discovery
    threading.Thread(target=udp_discovery_listener, args=(udp_port,), daemon=True).start()
    threading.Thread(target=udp_discovery_sender, args=(agent_id, agent_name, udp_port, tcp_port), daemon=True).start()

    # 4. Peer exchange (TCP)
    threading.Thread(target=peer_exchange, daemon=True).start()

    # вечный цикл (чтобы поток не завершался)
    while True:
        time.sleep(60)
