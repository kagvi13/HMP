# agents/peer_sync.py

import socket
import threading
import time
import json
import uuid
import ipaddress
import re
import netifaces
import select

from tools.storage import Storage
from datetime import datetime

storage = Storage()
my_id = storage.get_config_value("agent_id", str(uuid.uuid4()))
agent_name = storage.get_config_value("agent_name", "HMP-Agent")

# ======================
# Парсер host:port
# ======================
def parse_hostport(hostport):
    if hostport.startswith("["):  # IPv6
        m = re.match(r"\[(.+)\]:(\d+)$", hostport)
        if m:
            return m.group(1), int(m.group(2))
    else:  # IPv4
        if ":" in hostport:
            h, p = hostport.rsplit(":", 1)
            return h, int(p)
    return None, None

def is_ipv6(host: str) -> bool:
    return ":" in host

def is_loopback(host: str) -> bool:
    try:
        # IPv4 127.0.0.0/8
        if re.match(r"^127\.\d+\.\d+\.\d+$", host):
            return True
        # IPv6 ::1
        if host == "::1":
            return True
    except:
        pass
    return False

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
# Локальные IP (IPv4 + IPv6 link-local/global)
# ======================
def get_all_local_ips_v4():
    ips = []
    for iface in netifaces.interfaces():
        for addr in netifaces.ifaddresses(iface).get(netifaces.AF_INET, []):
            ip = addr.get("addr")
            if ip and not ip.startswith("127.") and not ip.startswith("0."):
                ips.append(ip)
    return ips

def get_all_local_ips_v6():
    ips = []
    for iface in netifaces.interfaces():
        for addr in netifaces.ifaddresses(iface).get(netifaces.AF_INET6, []):
            ip = addr.get("addr")
            # обрезаем суффикс %ifname у Windows/Linux
            if ip:
                ip = ip.split("%")[0]
                if ip != "::1":
                    ips.append(ip)
    return ips

# ======================
# Нормализация/расширение адресов для БД
# ======================
def expand_and_filter(addresses):
    out = []
    seen = set()
    for a in addresses:
        norm = storage.normalize_address(a)
        if not norm:
            continue
        try:
            proto, rest = norm.split("://", 1)
        except:
            continue
        host, _port = parse_hostport(rest)
        if not host or is_loopback(host):
            continue

        if proto == "tcp":
            cand = f"tcp://{rest}"
            if cand not in seen:
                out.append(cand); seen.add(cand)
        elif proto in ["udp", "utp", "any"]:
            for cand in (f"udp://{rest}", f"tcp://{rest}"):
                if cand not in seen:
                    out.append(cand); seen.add(cand)
    return out

# ======================
# UDP LAN Discovery (IPv4 broadcast + IPv6 multicast)
# ======================
def udp_lan_discovery():
    DISCOVERY_INTERVAL = 30

    local_addresses = storage.get_config_value("local_addresses", [])

    # Получаем уникальные порты из local_addresses
    udp_port_set = set()
    for a in local_addresses:
        _, port = parse_hostport(a.split("://", 1)[1])
        if port:
            udp_port_set.add(port)

    # ------------------ Слушатели ------------------
    listen_sockets = []
    for port in udp_port_set:
        # IPv4
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("", port))
            listen_sockets.append(sock)
            print(f"[UDP/LAN Discovery] слушаем IPv4 на *:{port}")
        except Exception as e:
            print(f"[UDP/LAN Discovery] Не удалось создать IPv4 сокет {port}: {e}")

        # IPv6
        try:
            sock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            sock6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock6.bind(("::", port))
            listen_sockets.append(sock6)
            print(f"[UDP/LAN Discovery] слушаем IPv6 на [::]:{port}")
        except Exception as e:
            print(f"[UDP/LAN Discovery] Не удалось создать IPv6 сокет {port}: {e}")

    msg_data = json.dumps({
        "id": my_id,
        "name": agent_name,
        "addresses": local_addresses
    }).encode("utf-8")

    while True:
        # ------------------ Приём ------------------
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
                print(f"[UDP/LAN Discovery] peer={peer_id} name={name} addresses={addresses} from {addr}")
            except Exception as e:
                print(f"[UDP/LAN Discovery] ошибка при приёме: {e}")

        # ------------------ Отправка ------------------
        for port in udp_port_set:
            # ---------------- IPv4 Broadcast ----------------
            for iface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET, [])
                for a in addrs:
                    if "broadcast" in a:
                        bcast = a["broadcast"]
                        try:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                            sock.sendto(msg_data, (bcast, port))
                            sock.close()
                            print(f"[UDP/LAN Discovery] -> IPv4 broadcast {bcast}:{port}")
                        except Exception as e:
                            print(f"[UDP/LAN Discovery] ошибка IPv4 broadcast {bcast}:{port}: {e}")

            # ---------------- IPv6 Multicast ----------------
            for iface in netifaces.interfaces():
                ifaddrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET6, [])
                for a in ifaddrs:
                    addr = a.get("addr")
                    if not addr:
                        continue

                    # Если link-local, добавляем scope_id
                    if addr.startswith("fe80:"):
                        multicast_addr = f"ff02::1%{iface}"
                    else:
                        multicast_addr = "ff02::1"

                    try:
                        sock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                        sock6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_IF, socket.if_nametoindex(iface))
                        sock6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, 1)
                        sock6.sendto(msg_data, (multicast_addr, port))
                        sock6.close()
                        print(f"[UDP/LAN Discovery] -> IPv6 multicast {multicast_addr}:{port}")
                    except Exception:
                        continue

        time.sleep(DISCOVERY_INTERVAL)

# ======================
# UDP Discovery Sender (глобальный v4/v6 мультикаст/бродкаст как было)
# ======================
def udp_discovery_sender():
    # IPv4 multicast
    sock4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock4.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    # IPv6 multicast
    try:
        sock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        sock6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, 2)
    except Exception:
        sock6 = None

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
                try:
                    sock4.sendto(json.dumps(msg).encode("utf-8"), ("239.255.0.1", port))
                except:
                    pass
                if sock6:
                    try:
                        sock6.sendto(json.dumps(msg).encode("utf-8"), ("ff02::1", port))
                    except:
                        pass

        if now - last_broadcast > BROADCAST_INTERVAL:
            try:
                sock4.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                for port in udp_port_set:
                    sock4.sendto(json.dumps(msg).encode("utf-8"), ("255.255.255.255", port))
            except:
                pass
            last_broadcast = now

        time.sleep(1)

# ==========================
# TCP Listener (IPv4 + IPv6, link-local + global)
# ==========================
def tcp_listener():
    sockets = []
    for host, port in tcp_ports:
        try:
            if is_ipv6(host):
                s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                bind_host = "::" if host in ["::", "any", "0.0.0.0"] else host
                s.bind((bind_host, port))
                s.listen(5)
                sockets.append(s)
                print(f"[TCP] Слушаем на [{bind_host}]:{port}")
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                bind_host = "" if host in ["0.0.0.0", "any"] else host
                s.bind((bind_host, port))
                s.listen(5)
                sockets.append(s)
                print(f"[TCP] Слушаем на {bind_host}:{port}")
        except Exception as e:
            print(f"[TCP] Ошибка bind/listen {host}:{port} -> {e}")

    while True:
        if not sockets:
            time.sleep(1)
            continue

        readable, _, _ = select.select(sockets, [], [], 1)
        for s in readable:
            try:
                conn, addr = s.accept()
                data = b""
                try:
                    data = conn.recv(1024) or b""
                except:
                    pass

                if data == b"PEER_EXCHANGE_REQUEST":
                    print(f"[TCP] PEER_EXCHANGE_REQUEST от {addr}")
                    try:
                        peers_list = []
                        for pid, addresses_json in storage.get_online_peers(limit=50):
                            try:
                                addresses = json.loads(addresses_json)
                            except:
                                addresses = []
                            addresses = expand_and_filter(addresses)
                            peers_list.append({"id": pid, "addresses": addresses})
                        payload = json.dumps(peers_list).encode("utf-8")
                        conn.sendall(payload)
                        print(f"[TCP] Отправлен список пиров ({len(peers_list)}) в {addr}")
                    except Exception as e:
                        print(f"[TCP] Ошибка при отправке списка пиров: {e}")
                conn.close()
            except Exception as e:
                print(f"[TCP] Ошибка при обработке соединения: {e}")

# ==========================
# Peer Exchange (инициатор TCP)
# ==========================
def peer_exchange():
    PEER_EXCHANGE_INTERVAL = 120
    while True:
        peers = storage.get_online_peers(limit=50)
        for peer in peers:
            peer_id, addresses_json = peer["id"], peer["addresses"]
            if peer_id == my_id:
                continue

            try:
                addr_list = json.loads(addresses_json)
            except:
                addr_list = []

            for addr in addr_list:
                norm = storage.normalize_address(addr)
                if not norm:
                    continue

                proto, hostport = norm.split("://")
                if proto not in ["tcp", "any"]:
                    continue

                host, port = parse_hostport(hostport)
                if not host or not port:
                    continue

                try:
                    # Для link-local IPv6 автоматически добавляем scope_id
                    if is_ipv6(host) and host.startswith("fe80:"):
                        for iface in get_all_local_ips_v6():  # перебор интерфейсов
                            if iface.endswith(host):  # простой вариант сопоставления
                                scope_id = socket.if_nametoindex(iface)
                                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                                sock.settimeout(3)
                                sock.connect((host, port, 0, scope_id))
                                break
                        else:
                            continue
                    else:
                        sock = socket.socket(socket.AF_INET6 if is_ipv6(host) else socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(3)
                        sock.connect((host, port))

                    sock.sendall(b"PEER_EXCHANGE_REQUEST")
                    data = sock.recv(64 * 1024)
                    sock.close()

                    if not data:
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
                                    "online"
                                )
                        print(f"[PeerExchange] Получено {len(peers_recv)} пиров от {host}:{port}")
                    except Exception as e:
                        print(f"[PeerExchange] Ошибка разбора ответа от {host}:{port} -> {e}")
                    break  # успешное соединение, не пробуем остальные адреса этого пира

                except Exception:
                    continue

        time.sleep(PEER_EXCHANGE_INTERVAL)

# ======================
# Основной запуск
# ======================
def start_sync():
    print("[PeerSync] Запуск фоновой синхронизации")
    storage.load_bootstrap()

    threading.Thread(target=udp_lan_discovery, daemon=True).start()
    threading.Thread(target=udp_discovery_sender, daemon=True).start()
    threading.Thread(target=peer_exchange, daemon=True).start()
    threading.Thread(target=tcp_listener, daemon=True).start()

    while True:
        time.sleep(60)