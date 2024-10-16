import time

for i in range(100):
    received_data=write_uart("01 05 A5 00 A5 00 94 56")

    #received_data = read_uart(timeout=1, num_bytes=8)  # 2秒超时，最多读取1024字节
    if received_data:
        print(f"读取到的数据: {received_data}")
    time.sleep(0.1)