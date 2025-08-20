# agents/peer_sync.py

import socket
import threading
import time
import json
import uuid
import ipaddress
import re
import netifaces
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
# IPv4 UDP LAN Discovery (приём + рассылка по /24)
# ======================
def udp_lan_discovery_v4():
    DISCOVERY_INTERVAL = 30
    local_addresses = storage.get_config_value("local_addresses", [])
    # порты, на которые слать/listen
    udp_port_set = set()
    for a in local_addresses:
        try:
            _proto, hostport = a.split("://", 1)
            _h, p = parse_hostport(hostport)
            if p:
                udp_port_set.add(p)
        except:
            continue

    # слушатели IPv4
    listen_sockets = []
    for port in udp_port_set:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("", port))
            listen_sockets.append(sock)
            print(f"[UDPv4] Слушаем UDP на 0.0.0.0:{port}")
        except Exception as e:
            print(f"[UDPv4] Не удалось слушать порт {port}: {e}")

    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.settimeout(0.5)

    while True:
        # --- приём ---
        for sock in listen_sockets:
            try:
                sock.settimeout(0.05)
                data, addr = sock.recvfrom(4096)
                msg = json.loads(data.decode("utf-8"))
                peer_id = msg.get("id")
                if not peer_id or peer_id == my_id:
                    continue
                name = msg.get("name", "unknown")
                addresses = msg.get("addresses", [])
                expanded = expand_and_filter(addresses)
                if expanded:
                    print(f"[UDPv4] RX от {addr} -> {expanded}")
                    storage.add_or_update_peer(peer_id, name, expanded, "discovery", "online")
            except socket.timeout:
                pass
            except Exception as e:
                print(f"[UDPv4] Ошибка при обработке пакета: {e}")

        # --- рассылка ---
        v4s = get_all_local_ips_v4()
        msg_data = json.dumps({"id": my_id, "name": agent_name, "addresses": local_addresses}).encode("utf-8")
        for local_ip in v4s:
            try:
                net = ipaddress.ip_network(local_ip + "/24", strict=False)
            except Exception:
                continue
            for ip in net.hosts():
                ip_str = str(ip)
                if ip_str == local_ip or ip_str.startswith("127.") or ip_str.startswith("0."):
                    continue
                for port in udp_port_set:
                    try:
                        send_sock.sendto(msg_data, (ip_str, port))
                    except:
                        pass

        time.sleep(DISCOVERY_INTERVAL)

# ======================
# IPv6 UDP Discovery (приём + мультикаст ff02::1)
# ======================
def udp_lan_discovery_v6():
    DISCOVERY_INTERVAL = 30
    local_addresses = storage.get_config_value("local_addresses", [])
    udp_port_set = set()
    for a in local_addresses:
        try:
            _proto, hostport = a.split("://", 1)
            h, p = parse_hostport(hostport)
            if p:
                udp_port_set.add(p)
        except:
            continue

    # слушатели IPv6
    listen_sockets = []
    for port in udp_port_set:
        try:
            sock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            sock6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock6.bind(("::", port))
            listen_sockets.append(sock6)
            print(f"[UDPv6] Слушаем UDP на [::]:{port}")
        except Exception as e:
            print(f"[UDPv6] Не удалось слушать порт {port}: {e}")

    # отправитель IPv6 (мультикаст link-local all-nodes)
    try:
        send_sock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        # hop limit 1
        send_sock6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, 1)
    except Exception as e:
        print(f"[UDPv6] Не удалось создать отправитель: {e}")
        send_sock6 = None

    maddr = "ff02::1"  # all-nodes on-link
    msg_data = json.dumps({"id": my_id, "name": agent_name, "addresses": local_addresses}).encode("utf-8")

    while True:
        # --- приём ---
        for sock in listen_sockets:
            try:
                sock.settimeout(0.05)
                data, addr = sock.recvfrom(8192)
                msg = json.loads(data.decode("utf-8"))
                peer_id = msg.get("id")
                if not peer_id or peer_id == my_id:
                    continue
                name = msg.get("name", "unknown")
                addresses = msg.get("addresses", [])
                expanded = expand_and_filter(addresses)
                if expanded:
                    print(f"[UDPv6] RX от {addr} -> {expanded}")
                    storage.add_or_update_peer(peer_id, name, expanded, "discovery", "online")
            except socket.timeout:
                pass
            except Exception as e:
                print(f"[UDPv6] Ошибка при обработке пакета: {e}")

        # --- мультикаст рассылка ---
        if send_sock6:
            for port in udp_port_set:
                try:
                    # iface scope index не задаём — ОС выберет подходящий on-link интерфейс
                    send_sock6.sendto(msg_data, (maddr, port))
                except:
                    pass

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

# ======================
# TCP Listener (v4+v6) для Peer Exchange
# ======================
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
                    chunk = conn.recv(1024)
                    data = chunk or b""
                except:
                    data = b""

                if data == b"PEER_EXCHANGE_REQUEST":
                    print(f"[TCP] PEER_EXCHANGE_REQUEST от {addr}")
                    try:
                        peers = []
                        for pid, addresses_json in storage.get_online_peers(limit=50):
                            try:
                                addresses = json.loads(addresses_json)
                            except Exception:
                                addresses = []
                            # фильтруем/расширяем перед отдачей
                            addresses = expand_and_filter(addresses)
                            peers.append({"id": pid, "addresses": addresses})
                        payload = json.dumps(peers).encode("utf-8")
                        conn.sendall(payload)
                        print(f"[TCP] Отправлен список пиров ({len(peers)}) в {addr}")
                    except Exception as e:
                        print(f"[TCP] Ошибка при отправке списка пиров: {e}")
                conn.close()
            except Exception as e:
                print(f"[TCP] Ошибка при обработке соединения: {e}")

# ======================
# Peer Exchange (TCP инициатор, читает ответ и пишет в БД)
# ======================
def peer_exchange():
    PEER_EXCHANGE_INTERVAL = 30  # почаще, чтобы быстрее раскидать пиров
    while True:
        rows = storage.get_online_peers(limit=50)
        for pid, addresses_json in rows:
            if pid == my_id:
                continue
            try:
                addr_list = json.loads(addresses_json)
            except:
                addr_list = []
            for addr in addr_list:
                norm = storage.normalize_address(addr)
                if not norm:
                    continue
                proto, hostport = norm.split("://", 1)
                if proto not in ["tcp", "any"]:
                    continue
                host, port = parse_hostport(hostport)
                if not host or not port or is_loopback(host):
                    continue

                try:
                    family = socket.AF_INET6 if is_ipv6(host) else socket.AF_INET
                    s = socket.socket(family, socket.SOCK_STREAM)
                    s.settimeout(3)
                    # IPv6 connect tuple принимает (host, port, flowinfo, scope_id), но flow/scope 0 по умолчанию ок
                    s.connect((host, port))
                    s.sendall(b"PEER_EXCHANGE_REQUEST")

                    # читаем весь ответ (до закрытия сокета/таймаута)
                    chunks = []
                    try:
                        while True:
                            b = s.recv(8192)
                            if not b:
                                break
                            chunks.append(b)
                    except socket.timeout:
                        pass
                    s.close()

                    if not chunks:
                        continue

                    try:
                        peers_list = json.loads(b"".join(chunks).decode("utf-8"))
                    except Exception as e:
                        print(f"[PeerExchange] ошибка парсинга ответа: {e}")
                        continue

                    for p in peers_list:
                        p_id = p.get("id")
                        if not p_id or p_id == my_id:
                            continue
                        addrs = expand_and_filter(p.get("addresses", []))
                        if addrs:
                            storage.add_or_update_peer(p_id, "unknown", addrs, "exchange", "online")
                            print(f"[PeerExchange] получили {p_id} -> {addrs}")

                    # если успешно отработали по одному TCP-адресу — дальше по этому пиру можно не перебирать
                    break
                except Exception as e:
                    # пробуем следующий адрес пира
                    continue
        time.sleep(PEER_EXCHANGE_INTERVAL)

# ======================
# Основной запуск
# ======================
def start_sync():
    print("[PeerSync] Запуск фоновой синхронизации")
    storage.load_bootstrap()

    threading.Thread(target=udp_lan_discovery_v4, daemon=True).start()
    threading.Thread(target=udp_lan_discovery_v6, daemon=True).start()
    threading.Thread(target=udp_discovery_sender, daemon=True).start()
    threading.Thread(target=peer_exchange, daemon=True).start()
    threading.Thread(target=tcp_listener, daemon=True).start()

    while True:
        time.sleep(60)
