

rhythm = [
    # 第一部分
    1, 1, 2, 0.5, 1, 2,  # Boom boom clap
    1, 1, 2, 0.5, 1, 2,  # Boom boom clap
    1, 1, 2, 0.5, 1, 2,  # Boom boom clap
    1, 1, 2, 0.5, 1, 2,  # Boom boom clap

    # 第二部分
    1, 1, 2, 0.5, 1, 2,  # Boom boom clap
    1, 1, 2, 0.5, 1, 2,  # Boom boom clap
    1, 1, 2, 0.5, 1, 2,  # Boom boom clap
    1, 1, 2, 0.5, 1, 2,  # Boom boom clap

    # 第三部分 (渐快)
    0.8, 0.8, 1.6, 0.4, 0.8, 1.6,  # Boom boom clap (稍快)
    0.8, 0.8, 1.6, 0.4, 0.8, 1.6,  # Boom boom clap (稍快)
    0.8, 0.8, 1.6, 0.4, 0.8, 1.6,  # Boom boom clap (稍快)
    0.8, 0.8, 1.6, 0.4, 0.8, 1.6,  # Boom boom clap (稍快)

    # 第四部分 (更快)
    0.6, 0.6, 1.2, 0.3, 0.6, 1.2,  # Boom boom clap (更快)
    0.6, 0.6, 1.2, 0.3, 0.6, 1.2,  # Boom boom clap (更快)
    0.6, 0.6, 1.2, 0.3, 0.6, 1.2,  # Boom boom clap (更快)
    0.6, 0.6, 1.2, 0.3, 0.6, 1.2,  # Boom boom clap (更快)
]


relay_on_command = "01 05 A5 00 A5 00 94 56"  # 开继电器
relay_off_command = "01 05 A5 00 A5 00 94 56"  # 开继电器
# 开始播放节奏

for duration in rhythm:
    write_uart(relay_on_command)  # 打开继电器
    time.sleep(duration* 0.1)  # 继电器保持开启状态的时间
    write_uart(relay_off_command)  # 关闭继电器
    time.sleep(duration* 0.1)  # 继电器保持关闭状态的时间
