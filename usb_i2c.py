import sys
import os
from ctypes import *

def CheckBit():
    """
    检查Python解释器的位数（32位或64位）。
    """
    if sys.maxsize > 2 ** 32:
        print("interpreter 64-bit")
        return 64
    else:
        print("interpreter 32-bit")
        return 32

def AddCWD():
    """
    将当前工作目录添加到DLL搜索路径。
    """
    os.add_dll_directory(os.getcwd())
    return os.getcwd()

def LoadDLL():
    """
    根据解释器的位数加载相应的DLL文件。
    """
    interpreterBit = CheckBit()
    cwd = AddCWD()
    ret = None
    dllPath = None
    if interpreterBit == 64:
        dllPath = "./CH341DLLA64.DLL"
    else:
        dllPath = "./CH341DLL.DLL"
    
    if os.path.exists(dllPath):
        try:
            ret = CDLL(dllPath)
        except OSError as e:
            print(f"Failed to load DLL: {e}")
    else:
        print(f"{dllPath} not found in {cwd}")
    return ret

class USBI2C:
    """
    用于与USB I2C设备通信的类。
    """
    ch341dll = LoadDLL()

    def __init__(self, usb_dev=0, i2c_dev=0x6C, i2c_speed=0x02):
        """
        初始化USBI2C对象。

        :param usb_dev: USB设备ID
        :param i2c_dev: I2C设备地址
        :param i2c_speed: I2C通信速度
        """
        self.usb_id = usb_dev
        self.update_device_address(i2c_dev)
        self.update_device_speed(i2c_speed)

    def update_device_address(self, i2c_dev):
        """
        更新I2C设备地址。

        :param i2c_dev: 新的I2C设备地址
        """
        self.dev_addr = i2c_dev * 2
        # if USBI2C.ch341dll.CH341OpenDevice(self.usb_id) != -1:
        #     USBI2C.ch341dll.CH341SetStream(self.usb_id, self.dev_addr)
        #     USBI2C.ch341dll.CH341CloseDevice(self.usb_id)
        # else:
        #     print("DEVICE INIT FAILED!!")

    def update_device_speed(self, i2c_speed):
        """
        更新I2C通信速度。

        :param i2c_speed: 新的I2C通信速度
        """
        if USBI2C.ch341dll.CH341OpenDevice(self.usb_id) != -1:
            USBI2C.ch341dll.CH341SetStream(self.usb_id, i2c_speed)
            USBI2C.ch341dll.CH341CloseDevice(self.usb_id)
        else:
            print("DEVICE INIT FAILED!!")

    def SendCmd(self, cmd, size):
        """
        发送命令到I2C设备。

        :param cmd: 命令字节列表
        :param size: 命令字节数
        :return: 返回读取的缓冲区数据
        """
        if USBI2C.ch341dll.CH341OpenDevice(self.usb_id) != -1:
            tcmd = (c_byte * (size + 1))()
            buffer = (c_byte * 300)()
            tcmd[0] = self.dev_addr
            for i in range(size):
                tcmd[i + 1] = cmd[i] & 0xFF

            USBI2C.ch341dll.CH341StreamI2C(self.usb_id, size + 1, tcmd, 300, buffer)
            USBI2C.ch341dll.CH341CloseDevice(self.usb_id)

            return buffer
        else:
            print("DEVICE OPERATE FAILED")
            return -1

    def read(self, addr):
        """
        从I2C设备读取数据。

        :param addr: 读取地址
        :return: 读取的数据
        """
        if USBI2C.ch341dll.CH341OpenDevice(self.usb_id) != -1:    
            obuf = (c_byte * 2)()
            ibuf = (c_byte * 1)()
            obuf[0] = self.dev_addr
            obuf[1] = addr
            USBI2C.ch341dll.CH341StreamI2C(self.usb_id, 2, obuf, 1, ibuf)
            USBI2C.ch341dll.CH341CloseDevice(self.usb_id)
            return ibuf[0] & 0xff
        else:
            print("USB CH341 Open Failed!")
            return 0

    def write(self, addr, dat):
        """
        向I2C设备写入数据。

        :param addr: 写入地址
        :param dat: 写入的数据
        """
        if USBI2C.ch341dll.CH341OpenDevice(self.usb_id) != -1:
            obuf = (c_byte * 3)()
            ibuf = (c_byte * 1)()
            obuf[0] = self.dev_addr
            obuf[1] = addr
            obuf[2] = dat & 0xff
            USBI2C.ch341dll.CH341StreamI2C(self.usb_id, 3, obuf, 0, ibuf)
            USBI2C.ch341dll.CH341CloseDevice(self.usb_id)
        else:
            print("USB CH341 Open Failed!")