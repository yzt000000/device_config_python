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
    def __init__(self,devices):
        super().__init__()
        self.instruments = devices
        self.init_ui()

    def init_ui(self):
        #self.rm = pyvisa.ResourceManager()
        try:
            self.rm = pyvisa.ResourceManager()
        except:
            self.rm = pyvisa.ResourceManager('@sim')
        #self.instruments = self.auto_detect_devices()
        #self.instruments = {
        #    'PVDD_device': self.rm.open_resource('GPIB0::1::INSTR'),  # 替换为控制 PVDD 的设备的资源字符串
        #    'CH_device'  : self.rm.open_resource('GPIB0::25::INSTR'),    # 替换为控制 CH1-CH4 的设备的资源字符串
        #}
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

    def auto_detect_devices(self):
        devices = {}
        resources = self.rm.list_resources()
        for resource in resources:
            try:
                instr = self.rm.open_resource(resource)
                try:
                    idn = instr.query('*IDN?').strip().lower()
                    if 'chroma' in idn:
                        devices['PVDD_device'] = instr
                except pyvisa.VisaIOError:
                    pass

                try:
                    idn = instr.query('ID?').strip().lower()
                    if 'hp6624a' in idn:
                        devices['CH_device'] = instr
                except pyvisa.VisaIOError:
                    pass
            except pyvisa.VisaIOError:
                pass
        return devices

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
