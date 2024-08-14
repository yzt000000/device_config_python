import serial
from serial.tools import list_ports




class USB_UART():

    def __init__(self):
        self.ports = list_ports.comports()
        for port in self.ports:
            print(f"Found port: {port.device}")

    def uart_write(self, hex_string):

        if self.ports:
            selected_port = self.ports[0].device
            print(f"Using port: {selected_port}")
            try:
                # 打开串口
                ser = serial.Serial(selected_port, baudrate=9600, timeout=1)
                # 16进制字符串
                #hex_string = "48 65 6C 6C 6F 20 53 65 72 69 61 6C 20 50 6F 72 74 21"  # "Hello Serial Port!"
                hex_bytes = bytes.fromhex(hex_string)
                # 发送16进制字符串
                ser.write(hex_bytes)
                print(f"Sent hex message: {hex_string}")
                # 关闭串口
                ser.close()
            except serial.SerialException as e:
                print(f"Error opening or using serial port: {e}")
        else:
            print("No serial ports found.")              
