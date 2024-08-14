# python gui app control i2c/uart/GPIB and other devices


## 0、Device config python 是什么

[Device Config Python]([https://github.com/yzt000000/device_config_python]) （Device Config Python ）是针对 CH341 I2C ，UART，GBIP电压控制的图形化程序。主要特性如下：

- 支持的功能包括：
    - 可配置的电源管理界面
    - 可配置的I2C device 地址，简单的读写，程序编辑窗口，程序执行、中断、恢复和终止。
    - 备用寄存器配置界面
    - 标准格式的寄存器表控制
    - 内建i2c、uart、电源控制函数

## 1、为什么选择 Device Config python

**** ：gui 内可以执行的python 脚本，可以load、save script， 也可以save clean log 信息

俗话说，工欲善其事，必先利其器。所以有时候做事效率低的原因也许是，你会用的工具种类太少。

**合作、贡献** ：开源软件的发展离不开大家的支持，欢迎大家多提建议，也希望更多的人一起参与进来，共同提高  ，同时把它推荐给更多有需要的朋友。

## 2、Device Config python 如何使用

- 1、Power： 勾选Enable Power Control 可开启电源控制界面。默认为关闭，没有相关设备的计算机在打开时会导致程序退出
- 2、main：主调试窗口
- 3、临时脚本：备用
- 4、Excel 查看器： regmap 读取，并可以按bit 配置
- 5. 说明






```python

#config I2C
read_i2c(0x00)
write_i2c(0x01, 0xAA)

#config UART
write_uart("00 05 00 01 10 11")

#config Power Supply
power_control.set_slew_rate("PVDD", 10)       #10v/ms
power_control.set_voltage("PVDD", 20.0)       #20V
power_control.toggle_power_func("CH1","ON")   # power on
power_control.toggle_power_func("CH2","OFF")  # power off
power_control.set_max_voltage("PVDD",30.0)    # voltage limit 
power_control.set_current("PVDD",1.0)         # set current limit to 1A


import time
time.sleep(0.1)
#for loop , adjust PVDD
for i in range(10):
    power_control.set_slew_rate("PVDD", 1000)
    time.sleep(5)
    power_control.set_voltage("PVDD", 200)

    time.sleep(5)
    power_control.set_slew_rate("PVDD", 500)
    time.sleep(5)
    power_control.set_voltage("PVDD", 0)
    time.sleep(5) 
```



### 2.6 许可

采用 GNU 开源协议，细节请阅读项目中的 LICENSE 文件内容。
