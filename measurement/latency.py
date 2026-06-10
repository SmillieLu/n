import subprocess
import re
import time


def ping(host, count=10, timeout=2):
    """
    跨平台ping测量，返回 (丢包率%, 平均时延ms)
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
    # 构建命令
    cmd = ['ping', param, str(count), timeout_param, str(timeout * 1000), host]
    try:
        output = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output

    # 解析丢包率
    loss = 100.0
    loss_match = re.search(r'(\d+)% loss', output) or re.search(r'丢包率.*?(\d+)%', output)
    if loss_match:
        loss = float(loss_match.group(1))

    # 解析平均时延
    avg = None
    avg_match = re.search(r'Average = (\d+)ms', output) or \
                re.search(r'平均值 = (\d+)ms', output) or \
                re.search(r'avg[\s/]+([\d.]+)', output, re.IGNORECASE)
    if avg_match:
        avg = float(avg_match.group(1))

    return loss, avg


def measure_with_jitter(host, count=20):
    """
    附加jitter测量：记录每次RTT，计算标准差作为抖动
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    cmd = ['ping', param, str(count), host]
    output = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
    # 提取所有time字段
    times = re.findall(r'time[=<](\d+)ms', output)
    if not times:
        return 100.0, None, None
    rtts = [float(t) for t in times]
    avg = sum(rtts) / len(rtts)
    variance = sum((r - avg) ** 2 for r in rtts) / len(rtts)
    jitter = variance ** 0.5
    loss = (count - len(rtts)) / count * 100
    return loss, avg, jitter