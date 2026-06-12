# 带宽测试（下行+上行）

import speedtest
import datetime
from src.utils import save_bandwidth_result, setup_logging

logger = setup_logging()

def run_bandwidth_test():
    """
    使用speedtest-cli测量下行和上行带宽
    返回结果字典，单位Mbps
    """
    try:
        logger.info("开始带宽测试，请稍候...（可能需要30秒）")
        st = speedtest.Speedtest()
        st.get_best_server()
        download_bps = st.download()          # bits per second
        upload_bps = st.upload()
        download_mbps = download_bps / 1_000_000
        upload_mbps = upload_bps / 1_000_000
        server = st.results.server['name'] + ", " + st.results.server['country']
        result = {
            "timestamp": datetime.datetime.now().isoformat(),
            "download_mbps": round(download_mbps, 2),
            "upload_mbps": round(upload_mbps, 2),
            "server": server
        }
        logger.info(f"带宽测试完成: 下行={download_mbps:.2f} Mbps, 上行={upload_mbps:.2f} Mbps")
        save_bandwidth_result(result)
        return result
    except Exception as e:
        logger.error(f"带宽测试失败: {e}")
        return None