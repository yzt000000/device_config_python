import sys
import os
from ctypes import *

def CheckBit():
    if sys.maxsize > 2 ** 32:
        print("interpreter 64-bit")
        return 64
    else:
        print("interpreter 32-bit")
        return 32

def AddCWD():
    os.add_dll_directory(os.getcwd())
    return os.getcwd()

def LoadDLL():
    interpreterBit = CheckBit()
    cwd = AddCWD()
    ret = None
    dllPath = None
    if interpreterBit == 64:
        dllPath = "./CH341DLLA64.DLL"
    else:
        dllPath = "CH3411DLL.DLL"
    if os.path.exists(cwd):
        try:
            ret = CDLL(dllPath)
        except OSError as e:
            print(e)
    else:
        print(cwd + " not exist")
    return ret

class USBI2C():
    ch341dll = LoadDLL()

    def __init__(self, usb_dev=0, i2c_dev=0x6C):
        self.usb_id = usb_dev
        self.update_device_address(i2c_dev)

    def update_device_address(self, i2c_dev):
        self.dev_addr = i2c_dev * 2
        if USBI2C.ch341dll.CH341OpenDevice(self.usb_id) != -1:
            USBI2C.ch341dll.CH341SetStream(self.usb_id, self.dev_addr)
            USBI2C.ch341dll.CH341CloseDevice(self.usb_id)
        else:
            print("DEVICE INIT FAILED!!")

    def SendCmd(self, cmd, size):
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
        if USBI2C.ch341dll.CH341OpenDevice(self.usb_id) != -1:    
            obuf = (c_byte * 2)()
            ibuf = (c_byte * 1)()
            obuf[0] = self.dev_addr
            obuf[1] = addr
            USBI2C.ch341dll.CH341StreamI2C(self.usb_id, 2, obuf, 1, ibuf)
            USBI2C.ch341dll.CH341CloseDevice(self.usb_id)
            #print("i2c read: 0x%x" % ibuf[0])
            print("read %2x=%2x"%(addr,ibuf[0] & 0xff))
            return ibuf[0] & 0xff

        else:
            print("USB CH341 Open Failed!")
            return 0

    def write(self, addr, dat):
        if USBI2C.ch341dll.CH341OpenDevice(self.usb_id) != -1:
            obuf = (c_byte * 3)()
            ibuf = (c_byte * 1)()
            obuf[0] = self.dev_addr
            obuf[1] = addr
            obuf[2] = dat & 0xff
            USBI2C.ch341dll.CH341StreamI2C(self.usb_id, 3, obuf, 0, ibuf)
            USBI2C.ch341dll.CH341CloseDevice(self.usb_id)
            #print("i2c write: 0x%x" % ibuf[0])
            print("write %2x=%2x"%(addr,dat))
        else:
            print("USB CH341 Open Failed!")
