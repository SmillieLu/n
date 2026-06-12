# 获取本机IP、掩码、网关、DNS、网段

import netifaces
import socket
import ipaddress
import platform
import subprocess
import re

def get_default_interface():
    """获取默认路由的网络接口名称"""
    gateways = netifaces.gateways()
    default = gateways['default']
    if netifaces.AF_INET in default:
        return default[netifaces.AF_INET][1]
    return None

def get_ip_and_netmask(iface):
    """获取指定接口的IPv4地址和子网掩码"""
    addrs = netifaces.ifaddresses(iface)
    if netifaces.AF_INET in addrs:
        for addr in addrs[netifaces.AF_INET]:
            if 'addr' in addr and 'netmask' in addr:
                return addr['addr'], addr['netmask']
    return None, None

def get_gateway():
    """获取默认网关IP"""
    gateways = netifaces.gateways()
    default = gateways['default']
    if netifaces.AF_INET in default:
        return default[netifaces.AF_INET][0]
    return None

def get_dns_servers():
    """获取DNS服务器地址（跨平台）"""
    dns_list = []
    system = platform.system()
    try:
        if system == "Windows":
            # 通过ipconfig命令解析
            output = subprocess.check_output("ipconfig /all", shell=True, text=True, encoding='gbk')
            lines = output.splitlines()
            for line in lines:
                if "DNS Servers" in line or "DNS 服务器" in line:
                    # 提取IP地址
                    parts = line.split(':')
                    if len(parts) >= 2:
                        ip = parts[1].strip()
                        if ip and ip not in dns_list:
                            dns_list.append(ip)
                elif line.strip() and line.strip()[0].isdigit() and '.' in line.strip():
                    # 部分Windows输出中DNS在下一行
                    ip_candidate = line.strip()
                    if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip_candidate):
                        if ip_candidate not in dns_list:
                            dns_list.append(ip_candidate)
        else:  # Linux / macOS
            with open("/etc/resolv.conf", "r") as f:
                for line in f:
                    if line.startswith("nameserver"):
                        ip = line.split()[1]
                        dns_list.append(ip)
    except Exception as e:
        print(f"获取DNS失败: {e}")
    return dns_list

def calculate_network(ip, netmask):
    """根据IP和掩码计算网段（CIDR格式）"""
    try:
        network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
        return str(network)
    except:
        return None

def get_all_network_info():
    """获取完整的网络基础信息"""
    iface = get_default_interface()
    if not iface:
        return {"error": "无法获取默认网络接口"}

    ip, mask = get_ip_and_netmask(iface)
    gateway = get_gateway()
    dns = get_dns_servers()
    network = calculate_network(ip, mask) if ip and mask else None

    info = {
        "interface": iface,
        "ip_address": ip,
        "subnet_mask": mask,
        "gateway": gateway,
        "dns_servers": dns,
        "network_segment": network,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
    return info

if __name__ == "__main__":
    info = get_all_network_info()
    for k, v in info.items():
        print(f"{k}: {v}")