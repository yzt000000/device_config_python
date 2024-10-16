import time

for i in range(100):
    #received_data=write_uart("01 05 A5 00 A5 00 94 56")
    #received_data=write_uart("01 05 00 01 FF 00 DD FA")
    #received_data=write_uart("01 05 00 01 FF 00 DD FA")
    #time.sleep(0.1)
    #received_data=write_uart("01 05 00 01 00 00 9C 0A")
    received_data=write_uart("01 05 00 00 FF 00 8C 3A")
    time.sleep(0.1)
    received_data=write_uart("01 05 00 00 00 00 CD CA")
    time.sleep(0.1)
    received_data=write_uart("01 05 00 01 FF 00 DD FA")
    time.sleep(0.1)
    received_data=write_uart("01 05 00 01 00 00 9C 0A")
    time.sleep(0.1)
    received_data=write_uart("01 05 00 02 FF 00 2D FA")
    time.sleep(0.1)
    received_data=write_uart("01 05 00 02 00 00 6C 0A")
    time.sleep(0.1)
    received_data=write_uart("01 05 00 03 FF 00 7C 3A")
    time.sleep(0.1)
    received_data=write_uart("01 05 00 03 00 00 3D CA")
    time.sleep(0.1)
    #time.sleep(1)
    #received_data=write_uart("01 05 00 00 00 00 CD CA")

    #received_data = read_uart(timeout=1, num_bytes=8)  # 2秒超时，最多读取1024字节
    #if received_data:
    #    print(f"读取到的数据: {received_data}")
    print("==========%3d============"%i)
    time.sleep(0.1)
