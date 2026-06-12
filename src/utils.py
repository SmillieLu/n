# 辅助工具（日志、文件写入）

import os
import csv
import datetime
import logging

def setup_logging(log_dir="logs"):
    """配置日志"""
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"measure_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("NetworkMeasure")

def save_ping_result(result_dict, result_dir="results"):
    """保存ping测量结果到CSV"""
    os.makedirs(result_dir, exist_ok=True)
    file_path = os.path.join(result_dir, "ping_results.csv")
    fieldnames = ["timestamp", "target", "packet_loss", "avg_rtt_ms", "min_rtt_ms", "max_rtt_ms"]
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(result_dict)

def save_bandwidth_result(bandwidth_dict, result_dir="results"):
    """保存带宽测试结果到CSV"""
    os.makedirs(result_dir, exist_ok=True)
    file_path = os.path.join(result_dir, "bandwidth_results.csv")
    fieldnames = ["timestamp", "download_mbps", "upload_mbps", "server"]
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(bandwidth_dict)

def save_network_info(info_dict, result_dir="results"):
    """保存网络基础信息到JSON（一次性）"""
    import json
    os.makedirs(result_dir, exist_ok=True)
    file_path = os.path.join(result_dir, "network_info.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(info_dict, f, indent=4, ensure_ascii=False)