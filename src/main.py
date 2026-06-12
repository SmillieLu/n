# 主程序入口

import threading
import time
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.network_info import get_all_network_info
from src.ping_test import periodic_ping
from src.bandwidth_test import run_bandwidth_test
from src.utils import setup_logging, save_network_info


def load_config(config_path="config.json"):
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    # 加载配置
    config = load_config()
    ping_cfg = config['ping']
    bw_cfg = config['bandwidth']

    # 初始化日志
    logger = setup_logging(config.get('log_dir', 'logs'))

    # 第一步：获取并保存本机网络信息（网段、网关、DNS）
    logger.info("=== 网络基础信息采集 ===")
    net_info = get_all_network_info()
    save_network_info(net_info)
    logger.info(f"IP地址: {net_info.get('ip_address')}")
    logger.info(f"子网掩码: {net_info.get('subnet_mask')}")
    logger.info(f"网段: {net_info.get('network_segment')}")
    logger.info(f"网关: {net_info.get('gateway')}")
    logger.info(f"DNS: {net_info.get('dns_servers')}")

    # 第二步：启动周期性Ping测试（后台线程）
    stop_event = threading.Event()
    ping_thread = threading.Thread(
        target=periodic_ping,
        args=(ping_cfg['target'], ping_cfg['count'], ping_cfg['interval_minutes'] * 60, stop_event),
        daemon=True
    )
    ping_thread.start()
    logger.info(f"已启动周期性Ping测试，每{ping_cfg['interval_minutes']}分钟一次")

    # 第三步：执行一次带宽测试
    if bw_cfg.get('enable', True):
        logger.info("=== 带宽测试（一次性） ===")
        run_bandwidth_test()
    else:
        logger.info("带宽测试已在配置中禁用")

    # 主线程保持运行，直到用户按下Ctrl+C
    logger.info("测量程序运行中，按 Ctrl+C 停止...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止...")
        stop_event.set()
        ping_thread.join(timeout=5)
        logger.info("程序已退出")


if __name__ == "__main__":
    main()