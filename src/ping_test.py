# 时延与丢包测量（含周期性调度）

import time
import subprocess
import re
import platform
import threading
from src.utils import save_ping_result, setup_logging
import datetime

logger = setup_logging()

def ping_host(host, count=4):
    """
    执行ping测试，返回丢包率和平均时延（毫秒）
    适用于Windows/Linux/macOS
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout = '-w' if platform.system().lower() == 'windows' else '-W'
    # Windows超时单位毫秒，Linux单位秒
    if platform.system().lower() == 'windows':
        cmd = ['ping', param, str(count), timeout, '3000', host]
    else:
        cmd = ['ping', param, str(count), timeout, '3', host]

    try:
        output = subprocess.check_output(cmd, universal_newlines=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        # ping可能返回非零（如全部丢包），但输出仍有信息
        output = e.output

    # 解析丢包率
    loss = None
    avg_rtt = None
    min_rtt = None
    max_rtt = None

    lines = output.splitlines()
    for line in lines:
        # 丢包率解析
        if "loss" in line.lower():
            # 格式: xx% loss 或 丢失 = xx%
            match = re.search(r'(\d+)%', line)
            if match:
                loss = float(match.group(1))
        # 时延解析：Windows: 平均 = 12ms，Linux: avg/最大值/最小值
        if "avg" in line.lower() or "平均" in line:
            # Windows格式: 最短 = 11ms，最长 = 12ms，平均 = 11ms
            match_avg = re.search(r'平均\s*=\s*(\d+)ms', line, re.IGNORECASE)
            if not match_avg:
                match_avg = re.search(r'avg[=/]\s*(\d+\.?\d*)\s*ms', line, re.IGNORECASE)
            if match_avg:
                avg_rtt = float(match_avg.group(1))
            # 提取min/max
            match_min = re.search(r'最短\s*=\s*(\d+)ms', line, re.IGNORECASE)
            if not match_min:
                match_min = re.search(r'min[=/]\s*(\d+\.?\d*)', line, re.IGNORECASE)
            if match_min:
                min_rtt = float(match_min.group(1))
            match_max = re.search(r'最长\s*=\s*(\d+)ms', line, re.IGNORECASE)
            if not match_max:
                match_max = re.search(r'max[=/]\s*(\d+\.?\d*)', line, re.IGNORECASE)
            if match_max:
                max_rtt = float(match_max.group(1))

    # 如果没有找到avg，尝试从rtt行提取（Linux风格）
    if avg_rtt is None:
        for line in lines:
            if "rtt" in line.lower():
                # 格式: rtt min/avg/max/mdev = 11.2/12.3/13.4/0.5 ms
                parts = line.split('=')
                if len(parts) > 1:
                    numbers = re.findall(r'(\d+\.?\d*)', parts[1])
                    if len(numbers) >= 3:
                        min_rtt = float(numbers[0])
                        avg_rtt = float(numbers[1])
                        max_rtt = float(numbers[2])
                        break

    # 如果丢包率仍为None，假设为0（无丢包指示时）
    if loss is None:
        loss = 0.0

    return {
        "packet_loss": loss,
        "avg_rtt_ms": avg_rtt if avg_rtt is not None else -1.0,
        "min_rtt_ms": min_rtt if min_rtt is not None else -1.0,
        "max_rtt_ms": max_rtt if max_rtt is not None else -1.0
    }

def periodic_ping(target, count=4, interval_seconds=600, stop_event=None):
    """
    周期性执行ping测量并保存结果
    interval_seconds: 间隔秒数（默认600=10分钟）
    """
    logger.info(f"开始周期性Ping测试：目标={target}，间隔={interval_seconds}秒，每次{count}个包")
    while not stop_event.is_set():
        timestamp = datetime.datetime.now().isoformat()
        result = ping_host(target, count)
        result['timestamp'] = timestamp
        result['target'] = target
        logger.info(f"Ping结果 -> 丢包率: {result['packet_loss']}%, 平均时延: {result['avg_rtt_ms']}ms")
        save_ping_result(result)
        # 等待下一个周期，期间每5秒检查一次停止信号
        for _ in range(interval_seconds // 5):
            if stop_event.is_set():
                break
            time.sleep(5)
        else:
            time.sleep(interval_seconds % 5)
    logger.info("Ping测试已停止")