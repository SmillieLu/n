import socket
import netifaces as ni
import subprocess
import re
import platform

def get_local_ip():
    """获取本机内网IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return socket.gethostbyname(socket.gethostname())

def get_netmask_and_network():
    """获取子网掩码并计算网段"""
    ip = get_local_ip()
    gateways = ni.gateways()
    if 'default' in gateways and ni.AF_INET in gateways['default']:
        default_iface = gateways['default'][ni.AF_INET][1]
        addrs = ni.ifaddresses(default_iface)
        if ni.AF_INET in addrs:
            for addr in addrs[ni.AF_INET]:
                if addr['addr'] == ip:
                    netmask = addr['netmask']
                    # 简化网段计算：取IP前三段 + .0/24（也可精确按掩码计算）
                    network = '.'.join(ip.split('.')[:3]) + '.0/24'
                    return netmask, network
    return None, None

def get_gateway():
    """获取默认网关"""
    gateways = ni.gateways()
    if 'default' in gateways and ni.AF_INET in gateways['default']:
        return gateways['default'][ni.AF_INET][0]
    return None

def get_dns():
    """跨平台获取DNS服务器"""
    system = platform.system()
    dns_list = []
    try:
        if system == 'Windows':
            output = subprocess.check_output(['ipconfig', '/all'], text=True)
            for line in output.splitlines():
                if 'DNS Servers' in line:
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        dns_list.append(match.group(1))
        else:  # Linux / macOS
            output = subprocess.check_output(['cat', '/etc/resolv.conf'], text=True)
            for line in output.splitlines():
                if line.startswith('nameserver'):
                    parts = line.split()
                    if len(parts) >= 2:
                        dns_list.append(parts[1])
    except Exception as e:
        dns_list = [str(e)]
    return dns_list if dns_list else ['无法获取']

def print_config():
    """打印所有网络配置"""
    print('=' * 50)
    print(f'本机IP    : {get_local_ip()}')
    netmask, network = get_netmask_and_network()
    if netmask:
        print(f'子网掩码  : {netmask}')
        print(f'网段      : {network}')
    print(f'默认网关  : {get_gateway()}')
    print(f'DNS服务器 : {", ".join(get_dns())}')
    print('=' * 50)

if __name__ == '__main__':
    print_config()