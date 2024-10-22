import sys
import random
import logging
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QSlider, QLabel, QLineEdit, QSizePolicy, QGridLayout
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
import pyvisa
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class power_switch_function():
    def __init__(self, devices):
        super().__init__()
        self.devices = devices
        self.instruments = {}  # 初始化为空字典
        self.init_ui()

    def init_ui(self):
        try:
            self.rm = pyvisa.ResourceManager()
        except:
            self.rm = pyvisa.ResourceManager('@sim')
        self.power_controls = {
            'PVDD': {'button': None, 'voltage_slider': None, 'current_slider': None, 'voltage_label': None, 'current_label': None, 'default_voltage': 144, 'device': 'PVDD_device',
                     'measured_voltage': None, 'measured_current': None, 'power': None, 'max_voltage_input': None, 'slew_slider': None, 'slew_label': None},
            'CH1': {'button': None, 'voltage_slider': None, 'current_slider': None, 'voltage_label': None, 'current_label': None, 'default_voltage': 33, 'device': 'CH_device',
                    'measured_voltage': None, 'measured_current': None, 'power': None, 'max_voltage_input': None, 'slew_slider': None, 'slew_label': None},
            'CH2': {'button': None, 'voltage_slider': None, 'current_slider': None, 'voltage_label': None, 'current_label': None, 'default_voltage': 33, 'device': 'CH_device',
                    'measured_voltage': None, 'measured_current': None, 'power': None, 'max_voltage_input': None, 'slew_slider': None, 'slew_label': None},
            'CH3': {'button': None, 'voltage_slider': None, 'current_slider': None, 'voltage_label': None, 'current_label': None, 'default_voltage': 33, 'device': 'CH_device',
                    'measured_voltage': None, 'measured_current': None, 'power': None, 'max_voltage_input': None, 'slew_slider': None, 'slew_label': None},
            'CH4': {'button': None, 'voltage_slider': None, 'current_slider': None, 'voltage_label': None, 'current_label': None, 'default_voltage': 33, 'device': 'CH_device',
                    'measured_voltage': None, 'measured_current': None, 'power': None, 'max_voltage_input': None, 'slew_slider': None, 'slew_label': None},
        }

    def open_devices(self):
        device_config = self.devices
        opened_devices = {}
        for device_name, device_info in device_config.items():
            try:
                # 提取 GPIB 地址
                address = str(device_info).split(' at ')[1]
                #address = device_info.split(' at ')[1]
            except IndexError:
                print(f"设备信息格式错误: {device_info}")
                continue
            opened_devices[device_name] = self.rm.open_resource(address)
        self.instruments = opened_devices

    def toggle_power(self, key):
        device = self.instruments[self.power_controls[key]['device']]
        button = self.power_controls[key]['button']
        if button.isChecked():
            if key == 'PVDD':
                # PVDD 的打开命令
                device.write('CONFigure:OUTPut ON')
                pass
            else:
                # CH1-CH4 的打开命令
                device.write(f'OUT {key[-1]},1')
                pass
            self.set_voltage(key, self.power_controls[key]['voltage_slider'].value())
        else:
            if key == 'PVDD':
                # PVDD 的关闭命令
                device.write('CONFigure:OUTPut OFF')
                pass
            else:
                # CH1-CH4 的关闭命令
                device.write(f'OUT {key[-1]},0')
                pass
    
    def set_voltage(self, key, value):
        device = self.instruments[self.power_controls[key]['device']]
        #voltage = value / 10.0
        voltage = value 
        if key == 'PVDD':
            # PVDD 的电压设置命令
            device.write(f'SOUR:VOLT {voltage}')
            pass
        else:
            # CH1-CH4 的电压设置命令
            device.write(f'VSET {key[-1]},{voltage}')
            pass
        #label = self.power_controls[key]['voltage_label']
        #label.setText(f'Set Voltage: {voltage} V')

    def set_current(self, key, value):
        device = self.instruments[self.power_controls[key]['device']]
        #current = value / 10.0
        current = value 
        if key == 'PVDD':
            # PVDD 的电流设置命令
            device.write( f'SOUR:CURR:PROT:HIGH {current}')
            pass
        else:
            pass
            # CH1-CH4 的电流设置命令
            device.write(f'CURR {key[-1]},{current}')
            device.write(f'OCP {key[-1]},1')
        #label = self.power_controls[key]['current_label']
        #label.setText(f'Set Current: {current} A')
    
    def set_slew_rate(self, key, value):
        device = self.instruments[self.power_controls[key]['device']]
        #slew_rate = value / 100.0
        slew_rate = value 
        if key == 'PVDD':
            # PVDD 的volt slow rate
            device.write(f'SOUR:VOLT:SLEW {slew_rate}')
            pass
        else:
            pass
            # CH1-CH4 的电流设置命令
            #device.write(f'CURR {key[-1]},{current}')
        #label = self.power_controls[key]['slew_label']
        #label.setText(f'Slew Rate: {slew_rate} V/ms')

    def set_max_voltage(self, key,max_voltage):
        try:
            device = self.instruments[self.power_controls[key]['device']]
            #max_voltage = float(self.power_controls[key]['max_voltage_input'].text()) * 10
            #self.power_controls[key]['voltage_slider'].setRange(0, int(max_voltage))
            #current = value / 10.0
            if key == 'PVDD':
                # PVDD 的电流设置命令
                #device.write(f'CURR {current}')
                device.write(f'SOUR:VOLT:LIMIT:HIGH {max_voltage}')
                #device.write(f'SOUR:VOLT:PROT:HIGH  {max_voltage}') 
                pass
            else:
                pass
                # CH1-CH4 的电流设置命令
                device.write(f'OVSET {key[-1]},{max_voltage}')

        except ValueError:
            pass  # 忽略无效输入

    def toggle_power_test(self, key,option):
        print(f"Key: {key}, Option: {option}")

    def toggle_power_func(self, key, option):
        device = self.instruments[self.power_controls[key]['device']]
        button = self.power_controls[key]['button']
        if key == 'PVDD':
            # PVDD 的打开命令
            if(option == 'ON'):
                device.write('CONFigure:OUTPut ON')
            else:
                device.write('CONFigure:OUTPut OFF')
        else:
            # CH1-CH4 的打开命令
            if(option == 'ON'):
                device.write(f'OUT {key[-1]},1')
            else:
                device.write(f'OUT {key[-1]},0')
        #self.set_voltage(key, self.power_controls[key]['voltage_slider'].value())

    def set_current_prot(self, key, value):
        device = self.instruments[self.power_controls[key]['device']]
        current = value 
        if key == 'PVDD':
            # PVDD 的电流设置命令
            device.write( f'SOUR:CURR:PROT:HIGH {current}')
            #device.write( f'SOUR:CURR:LIMIT:HIGH {current}')
            #device.write( f'SOUR:CURR {current}')
            pass
        else:
            pass
            # CH1-CH4 的电流设置命令
            #device.write(f'CURR {key[-1]},{current}')
            if(value >0) :
                device.write(f'OCP {key[-1]},1')
            else:
                device.write(f'OCP {key[-1]},0')


    def set_current_limit(self, key, value):
        device = self.instruments[self.power_controls[key]['device']]
        current = value 
        if key == 'PVDD':
            # PVDD 的电流设置命令
            #device.write( f'SOUR:CURR:PROT:HIGH {current}')
            device.write( f'SOUR:CURR:LIMIT:HIGH {current}')
            #device.write( f'SOUR:CURR {current}')
            pass
        else:
            pass
            # CH1-CH4 的电流设置命令
            #device.write(f'CURR {key[-1]},{current}')
            #device.write(f'OCP {key[-1]},1')
            if(value >0) :
                device.write(f'OCP {key[-1]},1')
            else:
                device.write(f'OCP {key[-1]},0')

    def read_voltage(self, key):
        device = self.instruments[self.power_controls[key]['device']]
        try:
            if key == 'PVDD':
                measured_voltage = float(device.query('FETC:VOLT?'))
            else:
                channel = key[-1]
                measured_voltage = float(device.query(f'VOUT? {channel}').replace('\n','').replace('\r',''))
            return measured_voltage
        except pyvisa.VisaIOError:
            print(f"读取{key}电压时发生错误")
            return None

    def read_current(self, key):
        device = self.instruments[self.power_controls[key]['device']]
        try:
            if key == 'PVDD':
                measured_current = float(device.query('FETC:CURR?'))
            else:
                channel = key[-1]
                measured_current = float(device.query(f'IOUT? {channel}').replace('\n','').replace('\r',''))
            return measured_current
        except pyvisa.VisaIOError:
            print(f"读取{key}电流时发生错误")
            return None

    def read_power(self, key):
        voltage = self.read_voltage(key)
        current = self.read_current(key)
        if voltage is not None and current is not None:
            return voltage * current
        else:
            return None