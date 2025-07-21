import socket
import requests

def get_internal_ips():
    ips = []
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
        ips.append(ip)
    except:
        pass
    try:
        # Вытягиваем IP со всех интерфейсов
        for info in socket.getaddrinfo(hostname, None):
            addr = info[4][0]
            if addr not in ips and ':' not in addr:
                ips.append(addr)
    except:
        pass
    return ips

def get_external_ip():
    try:
        ip4 = requests.get("https://api.ipify.org").text
        ip6 = requests.get("https://api64.ipify.org").text
        return ip4, ip6
    except:
        return None, None

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(("0.0.0.0", port))
    sock.close()
    return result == 0

if __name__ == "__main__":
    print("🔍 Диагностика HMP-агента\n")

    print("📡 Внутренние IP-адреса:")
    for ip in get_internal_ips():
        print(f"  - {ip}")

    ip4, ip6 = get_external_ip()
    print("\n🌍 Внешние IP:")
    print(f"  - IPv4: {ip4 or '❌'}")
    print(f"  - IPv6: {ip6 or '❌'}")

    port = 22555
    print(f"\n🔌 Проверка порта DHT ({port}): {'🟢 открыт' if check_port(port) else '🔴 закрыт'}")
