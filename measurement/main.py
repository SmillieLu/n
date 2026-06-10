import schedule
import time
import csv
import os
from datetime import datetime
from measurement import config, latency

HOST = '8.8.8.8'  # 测试目标，可按需改为网关或公网地址
OUTPUT_DIR = 'data'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def measure_and_save():
    """执行测量并保存到CSV文件"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    loss, avg, jitter = latency.measure_with_jitter(HOST, count=20)

    data = [timestamp, HOST, loss, avg, jitter]
    file_path = os.path.join(OUTPUT_DIR, f'latency_{datetime.now().strftime("%Y%m%d")}.csv')

    file_exists = os.path.isfile(file_path)
    with open(file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'Host', 'Loss%', 'AvgLatency(ms)', 'Jitter(ms)'])
        writer.writerow(data)
    print(f'[{timestamp}] 丢包率: {loss}%, 平均时延: {avg}ms, Jitter: {jitter}ms')


if __name__ == '__main__':
    print('网络测量调度启动，按 Ctrl+C 停止...')
    # 立即执行一次
    measure_and_save()
    # 每小时执行一次（分钟可根据需求设为0）
    schedule.every(1).hours.at(':00').do(measure_and_save)
    # 如需更多时段（如每30分钟），可追加：schedule.every(30).minutes.do(...)
    while True:
        schedule.run_pending()
        time.sleep(60)