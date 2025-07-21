# agents/tools/diagnose.py

import socket
import requests

def get_internal_ips():
    ips = set()
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
        ips.add(ip)
    except:
        pass
    try:
        for info in socket.getaddrinfo(hostname, None):
            addr = info[4][0]
            if ':' not in addr:  # фильтрация IPv6 для простоты
                ips.add(addr)
    except:
        pass
    return list(ips)

def get_external_ip():
    try:
        ip4 = requests.get("https://api.ipify.org").text
    except:
        ip4 = None
    try:
        ip6 = requests.get("https://api64.ipify.org").text
    except:
        ip6 = None
    return ip4, ip6

def check_port_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex(("0.0.0.0", port))
        return result == 0
    finally:
        sock.close()

def run_diagnose(port=22555):
    print("🔍 Диагностика HMP-агента\n")

    print("📡 Внутренние IP-адреса:")
    for ip in get_internal_ips():
        print(f"  - {ip}")

    ip4, ip6 = get_external_ip()
    print("\n🌍 Внешние IP:")
    print(f"  - IPv4: {ip4 or '❌'}")
    print(f"  - IPv6: {ip6 or '❌'}")

    print(f"\n🔌 Проверка порта DHT ({port}): {'🟢 открыт' if check_port_open(port) else '🔴 закрыт'}")

if __name__ == "__main__":
    run_diagnose()
