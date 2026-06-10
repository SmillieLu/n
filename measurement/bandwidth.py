# measurement/bandwidth_speedtest.py
import speedtest

def test_bandwidth():
    st = speedtest.Speedtest()
    st.get_best_server()
    download_bps = st.download()        # 单位: bits/sec
    upload_bps = st.upload()
    # 转换为 Mbps
    down_mbps = download_bps / 1_000_000
    up_mbps = upload_bps / 1_000_000
    return down_mbps, up_mbps

if __name__ == '__main__':
    down, up = test_bandwidth()
    print(f'下载速度: {down:.2f} Mbps, 上传速度: {up:.2f} Mbps')