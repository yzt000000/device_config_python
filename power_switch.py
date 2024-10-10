import sys
import random
import logging
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QSlider, QLabel, QLineEdit, QSizePolicy, QGridLayout,QComboBox
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal,QObject
import pyvisa
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from time import time
from queue import Queue, Empty
from threading import Event

from PyQt5.QtCore import QMutex, QMutexLocker

class ErrorHandler(QObject):
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.error_queue = Queue()

    def handle_error(self, error_message):
        self.error_queue.put(error_message)
        self.error_signal.emit(error_message)

class MeasurementThread(QThread):
    measurement_signal = pyqtSignal(str, float, float, float)
    power_status_signal = pyqtSignal(str, bool)
    measurement_complete = pyqtSignal()

    def __init__(self, instruments, power_controls, error_handler):
        super().__init__()
        self.instruments = instruments
        self.power_controls = power_controls
        self.running = False
        self.measurement_requested = Event()
        self.error_handler = error_handler

    def run(self):
        self.running = True
        while self.running:
            self.measurement_requested.wait()
            if not self.running:
                break
            self.measurement_requested.clear()
            self.perform_measurement()
            self.measurement_complete.emit()

    def perform_measurement(self):
        for key, control in self.power_controls.items():
            if not self.running:
                break

            device = self.instruments[control['device']]

            try:
                # Check power status
                if key == 'PVDD':
                    device.write('*CLS')
                    status = device.query('CONFigure:OUTPut?')
                    power_on = 'ON' in status
                else:
                    channel = key[-1]
                    status = device.query(f'OUT? {channel}')
                    power_on = '1' in status

                self.power_status_signal.emit(key, power_on)

                # Measure voltage, current, and power
                if key == 'PVDD':
                    measured_voltage = float(device.query('FETC:VOLT?'))
                    measured_current = float(device.query('FETC:CURR?'))
                else:
                    channel = key[-1]
                    measured_voltage = float(device.query(f'VOUT? {channel}').replace('\n','').replace('\r',''))
                    measured_current = float(device.query(f'IOUT? {channel}').replace('\n','').replace('\r',''))
                power = measured_voltage * measured_current
                self.measurement_signal.emit(key, measured_voltage, measured_current, power)

            except pyvisa.VisaIOError as e:
                self.error_handler.handle_error(f"Error communicating with {key}: {str(e)}")

    def stop(self):
        self.running = False
        self.measurement_requested.set()  # Wake up the thread to exit

    def request_measurement(self):
        self.measurement_requested.set()




class PowerSupplyControl(QWidget):
    def __init__(self,devices):
        super().__init__()
        #self.instruments = devices
        self.devices = devices
        #self.init_ui()
        self.initialized = False  # 添加一个标志来检查是否已经被初始化
        self.error_handler = ErrorHandler()
        self.error_handler.error_signal.connect(self.display_error)


    def init_ui(self):
        if self.initialized:
            return
        self.initialized = True
        self.rm = pyvisa.ResourceManager()
        #self.instruments = self.auto_detect_devices()
        self.instruments = self.open_devices(self.devices)

        self.layout = QVBoxLayout()
        self.power_controls = {
            'PVDD': {'button': None, 'voltage_slider': None, 'current_slider': None, 'voltage_label': None, 'current_label': None, 'default_voltage': 1440, 'device': 'PVDD_device',
                     'measured_voltage': None, 'measured_current': None, 'power': None, 'max_voltage_input': None, 'slew_slider': None, 'slew_label': None, 'default_max_voltage': 14.4 , 'max_current_input': None, 'default_max_current': 60.0, 'default_current':600},
            'CH1': {'button': None, 'voltage_slider': None, 'current_slider': None, 'voltage_label': None, 'current_label': None, 'default_voltage': 330, 'device': 'CH_device',
                    'measured_voltage': None, 'measured_current': None, 'power': None, 'max_voltage_input': None, 'slew_slider': None, 'slew_label': None, 'default_max_voltage': 3.3, 'max_current_input': None, 'default_max_current': 60.0, 'default_current': 600},
            'CH2': {'button': None, 'voltage_slider': None, 'current_slider': None, 'voltage_label': None, 'current_label': None, 'default_voltage': 1440, 'device': 'CH_device',
                    'measured_voltage': None, 'measured_current': None, 'power': None, 'max_voltage_input': None, 'slew_slider': None, 'slew_label': None, 'default_max_voltage': 14.4, 'max_current_input': None, 'default_max_current': 60.0, 'default_current': 600},
            'CH3': {'button': None, 'voltage_slider': None, 'current_slider': None, 'voltage_label': None, 'current_label': None, 'default_voltage': 330, 'device': 'CH_device',
                    'measured_voltage': None, 'measured_current': None, 'power': None, 'max_voltage_input': None, 'slew_slider': None, 'slew_label': None, 'default_max_voltage': 3.3, 'max_current_input': None, 'default_max_current': 60.0, 'default_current': 600},
            'CH4': {'button': None, 'voltage_slider': None, 'current_slider': None, 'voltage_label': None, 'current_label': None, 'default_voltage': 330, 'device': 'CH_device',
                    'measured_voltage': None, 'measured_current': None, 'power': None, 'max_voltage_input': None, 'slew_slider': None, 'slew_label': None, 'default_max_voltage': 3.3, 'max_current_input': None, 'default_max_current': 60.0, 'default_current': 600},
        }

        # Add control panel for measurement
        control_group = self.create_measurement_control_group()
        #control_group.setStyleSheet("border: 1px solid black;")  # 添加边框
        self.layout.addWidget(control_group)

        pvdd_group = self.create_power_control_group('PVDD')
        self.layout.addWidget(pvdd_group)

        ch_layout = QHBoxLayout()
        for key in ['CH1', 'CH2', 'CH3', 'CH4']:
            ch_layout.addWidget(self.create_power_control_group(key))
        self.layout.addLayout(ch_layout)

        self.setLayout(self.layout)
        self.setWindowTitle('Power Supply Control')

        self.measurement_thread = MeasurementThread(self.instruments, self.power_controls, self.error_handler)
        self.measurement_thread.measurement_signal.connect(self.update_measurements)
        self.measurement_thread.power_status_signal.connect(self.update_power_status)
        self.measurement_thread.measurement_complete.connect(self.on_measurement_complete)

        self.measurement_timer = QTimer(self)
        self.measurement_timer.timeout.connect(self.request_measurement)

        # Add error checking timer
        self.error_check_timer = QTimer(self)
        self.error_check_timer.timeout.connect(self.check_errors)
        self.error_check_timer.start(100)  # Check for errors every 100 ms




    def open_devices(self, device_config):
        opened_devices = {}
        for device_name, device_info in device_config.items():
            # 提取 GPIB 地址
            address = str(device_info).split(' at ')[1]
            opened_devices[device_name] = self.rm.open_resource(address)
        return opened_devices
    
    def update_power_status(self, key, power_on):
        button = self.power_controls[key]['button']
        button.setChecked(power_on)
        if power_on:
            self.set_voltage(key, self.power_controls[key]['voltage_slider'].value())

    

    def create_power_control_group(self, key):
        group_box = QGroupBox(key)
        group_layout = QVBoxLayout()

        button = QPushButton('Power')
        button.setCheckable(True)
        button.clicked.connect(lambda checked, k=key: self.toggle_power(k))
        button.setFixedSize(200, 35)
        group_layout.addWidget(button)

        button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border: 2px solid black;
                padding: 10px;
                font-weight: bold;
                width: 200px;
                height: 35px;
            }
            QPushButton:checked {
                background-color: green;
            }
        """)

        #Voltage setting
        voltage_layout = QHBoxLayout()

        voltage_slider = QSlider(Qt.Horizontal)
        voltage_slider.setRange(0, self.power_controls[key]['default_voltage'])
        voltage_slider.setValue(self.power_controls[key]['default_voltage'])
        voltage_slider.valueChanged.connect(lambda value, k=key: self.set_voltage(k, value))
        voltage_slider.setFixedSize(200, 20)
        voltage_layout.addWidget(voltage_slider)

        max_voltage_input = QLineEdit()
        max_voltage_input.setPlaceholderText("Max Voltage (V)")
        #max_voltage_input.setText("14.4")
        max_voltage_input.setText(str(self.power_controls[key]['default_max_voltage']))
        max_voltage_input.returnPressed.connect(lambda k=key: self.set_max_voltage(k))
        max_voltage_input.setFixedSize(40, 20)
        voltage_layout.addWidget(max_voltage_input)

        voltage_layout.addStretch()
        group_layout.addLayout(voltage_layout)

        voltage_label = QLabel(f'Set Voltage: {self.power_controls[key]["default_voltage"] / 100.0} V')
        group_layout.addWidget(voltage_label)

        #Current setting
        current_layout = QHBoxLayout()

        current_slider = QSlider(Qt.Horizontal)
        current_slider.setRange(0, self.power_controls[key]['default_current'])
        current_slider.setValue(self.power_controls[key]['default_current'])
        current_slider.valueChanged.connect(lambda value, k=key: self.set_current(k, value))
        current_slider.setFixedSize(200, 20)
        #group_layout.addWidget(current_slider)
        current_layout.addWidget(current_slider)

        max_current_input = QLineEdit()
        max_current_input.setPlaceholderText("Max Current (A)")
        max_current_input.setText(str(self.power_controls[key]['default_max_current']))
        max_current_input.returnPressed.connect(lambda k=key: self.set_max_current(k))
        max_current_input.setFixedSize(40, 20)
        current_layout.addWidget(max_current_input)

        current_layout.addStretch()
        group_layout.addLayout(current_layout)

        #current_label = QLabel('Set Current: 1 A')
        current_label = QLabel(f'Set Current: {self.power_controls[key]["default_current"] / 10.0} A')
        group_layout.addWidget(current_label)

        #slew rate setting

        slew_slider = QSlider(Qt.Horizontal)
        slew_slider.setRange(1, 100)
        slew_slider.setValue(1)
        slew_slider.valueChanged.connect(lambda value, k=key: self.set_slew_rate(k, value))
        slew_slider.setFixedSize(200, 20)
        group_layout.addWidget(slew_slider)

        slew_label = QLabel('Slew Rate: 1 V/ms')
        group_layout.addWidget(slew_label)

        measured_voltage = QLabel('Measured Voltage: -- V')
        measured_current = QLabel('Measured Current: -- A')
        power = QLabel('Power: -- W')
        group_layout.addWidget(measured_voltage)
        group_layout.addWidget(measured_current)
        group_layout.addWidget(power)

        power_curve_figure = Figure()
        power_curve_canvas = FigureCanvas(power_curve_figure)
        power_curve_ax = power_curve_figure.add_subplot(111)
        power_curve_ax.set_xlim(0, 60)
        power_curve_ax.set_ylim(0, 100)
        power_curve_ax.set_xlabel('Time (s)')
        power_curve_ax.set_ylabel('Power (W)')
        power_curve_ax.grid(True)
        power_curve_line, = power_curve_ax.plot([], [], label=f'{key} Power')
        power_curve_ax.legend()
        power_curve_canvas.draw()

        group_layout.addWidget(power_curve_canvas)

        group_box.setLayout(group_layout)

        self.power_controls[key]['button'] = button
        self.power_controls[key]['voltage_slider'] = voltage_slider
        self.power_controls[key]['current_slider'] = current_slider
        self.power_controls[key]['voltage_label'] = voltage_label
        self.power_controls[key]['current_label'] = current_label
        self.power_controls[key]['max_voltage_input'] = max_voltage_input
        self.power_controls[key]['max_current_input'] = max_current_input
        self.power_controls[key]['slew_slider'] = slew_slider
        self.power_controls[key]['slew_label'] = slew_label
        self.power_controls[key]['measured_voltage'] = measured_voltage
        self.power_controls[key]['measured_current'] = measured_current
        self.power_controls[key]['power'] = power
        self.power_controls[key]['power_curve_canvas'] = power_curve_canvas
        self.power_controls[key]['power_curve_ax'] = power_curve_ax
        self.power_controls[key]['power_curve_line'] = power_curve_line
        self.power_controls[key]['power_curve_x_data'] = []
        self.power_controls[key]['power_curve_y_data'] = []

        return group_box




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
        voltage = value / 100.0
        if key == 'PVDD':
            # PVDD 的电压设置命令
            device.write(f'SOUR:VOLT {voltage}')
            pass
        else:
            # CH1-CH4 的电压设置命令
            device.write(f'VSET {key[-1]},{voltage}')
            pass
        label = self.power_controls[key]['voltage_label']
        label.setText(f'Set Voltage: {voltage} V')

    def set_current(self, key, value):
        device = self.instruments[self.power_controls[key]['device']]
        max_current = float(self.power_controls[key]['max_current_input'].text())
        current = value/10.0 
        if key == 'PVDD':
            # PVDD 的电流设置命令
            #device.write( f'SOUR:CURR:PROT:HIGH {current}')
            #device.write( f'SOUR:CURR:LIMIT:HIGH {current}')
            device.write( f'SOUR:CURR {current}')
            pass
        else:
            pass
            # CH1-CH4 的电流设置命令
            device.write(f'CURR {key[-1]},{current}')
            device.write(f'OCP {key[-1]},1')
        label = self.power_controls[key]['current_label']
        label.setText(f'Set Current: {current} A')
    
    def set_slew_rate(self, key, value):
        device = self.instruments[self.power_controls[key]['device']]
        slew_rate = value / 100.0
        if key == 'PVDD':
            # PVDD 的volt slow rate
            device.write(f'SOUR:VOLT:SLEW {slew_rate}')
            pass
        else:
            pass
            # CH1-CH4 的电流设置命令
            #device.write(f'CURR {key[-1]},{current}')
        label = self.power_controls[key]['slew_label']
        label.setText(f'Slew Rate: {slew_rate} V/ms')

    def set_max_voltage(self, key):
        try:
            device = self.instruments[self.power_controls[key]['device']]
            max_voltage = float(self.power_controls[key]['max_voltage_input'].text()) * 100
            self.power_controls[key]['voltage_slider'].setRange(0, int(max_voltage))
            #current = value / 10.0
            if key == 'PVDD':
                # PVDD 的电流设置命令
                #device.write(f'CURR {current}')
                #device.write(f'SOUR:VOLT:LIMIT:HIGH {max_voltage}')
                device.write(f'SOUR:VOLT:PROT:HIGH  {max_voltage}') 
                pass
            else:
                pass
                # CH1-CH4 的电流设置命令
                device.write(f'OVSET {key[-1]},{max_voltage}')

        except ValueError:
            pass  # 忽略无效输入

    def set_max_current(self, key):
        try:
            device = self.instruments[self.power_controls[key]['device']]
            max_current = float(self.power_controls[key]['max_current_input'].text()) * 10
            self.power_controls[key]['current_slider'].setRange(1, int(max_current))
            if key == 'PVDD':
                # PVDD 的最大电流设置命令
                #device.write(f'SOUR:CURR:PROT:HIGH {max_current / 10}')
                device.write(f'SOUR:CURR:LIMIT:HIGH {max_current / 10}')
            else:
                # CH1-CH4 的最大电流设置命令
                device.write(f'OCP {key[-1]},{max_current / 10}')
        except ValueError:
            pass  # 忽略无效输入

    def create_measurement_control_group(self):
        group = QGroupBox("Measurement Control")
        layout = QHBoxLayout()

        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.clicked.connect(self.toggle_measurement)
        layout.addWidget(self.start_stop_button)

        layout.addWidget(QLabel("Update Interval:"))
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["1s", "10s", "60s", "600s"])
        self.interval_combo.currentIndexChanged.connect(self.change_update_interval)
        layout.addWidget(self.interval_combo)

        # 设置布局的高度
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        group.setLayout(layout)
        return group        

    def toggle_measurement(self):
        if self.measurement_thread.isRunning():
            self.measurement_thread.stop()
            self.measurement_timer.stop()
            self.measurement_thread.wait()
            self.start_stop_button.setText("Start")
            self.start_stop_button.setStyleSheet("background-color: red")
            
        else:
            interval = int(self.interval_combo.currentText()[:-1])
            self.measurement_thread.start()
            self.measurement_timer.start(interval * 1000)  # Convert to milliseconds
            #self.start_stop_button.setText("Stop")
            self.start_stop_button.setText("Running")
            self.start_stop_button.setStyleSheet("background-color: green")
            self.request_measurement()  # Start the first measurement immediately

    def change_update_interval(self):
        interval = int(self.interval_combo.currentText()[:-1])
        if self.measurement_timer.isActive():
            self.measurement_timer.setInterval(interval * 1000)  # Convert to milliseconds

    def request_measurement(self):
        self.measurement_thread.request_measurement()

    def on_measurement_complete(self):
        # This method is called when a measurement is complete
        # You can add any post-measurement logic here if needed
        pass       


    def schedule_measurement(self):
        if not self.measurement_thread.measurement_complete.is_set():
            print("Warning: Previous measurement not complete. Skipping this cycle.")
            return
        self.measurement_thread.measurement_complete.clear()
        self.measurement_thread.schedule_measurement()
        
    def closeEvent(self, event):
        if self.measurement_thread.isRunning():
            self.measurement_thread.stop()
            self.measurement_timer.stop()
            self.measurement_thread.wait()
        super().closeEvent(event)

    # def handle_error(self, error_message):
    #     print(f"Error: {error_message}")


    def display_error(self, error_message):
        print(f"Error: {error_message}")
        # You can also update GUI here to display the error, if needed

    def check_errors(self):
        try:
            while True:
                error = self.error_handler.error_queue.get_nowait()
                self.display_error(error)
        except Empty:
            pass


    def update_measurements(self, key, voltage, current, power):
        # 更新测量值标签
        self.power_controls[key]['measured_voltage'].setText(f'Measured Voltage: <b>{voltage:.2f}</b> V')
        self.power_controls[key]['measured_current'].setText(f'Measured Current: <b>{current:.2f}</b> A')
        self.power_controls[key]['power'].setText(f'Power: {power:.2f} W')

        # 获取当前时间戳
        current_time = time()  # 当前时间戳（秒）

        # 获取曲线图数据
        x_data = self.power_controls[key]['power_curve_x_data']
        y_data = self.power_controls[key]['power_curve_y_data']

        # 添加新的数据点
        x_data.append(current_time)
        y_data.append(power)

        # 移除超出60秒的数据
        max_time = 60
        while x_data and x_data[0] < current_time - max_time:
            x_data.pop(0)
            y_data.pop(0)

        # 更新图表
        self.power_controls[key]['power_curve_line'].set_data(x_data, y_data)

        # 设置 X 轴的范围，确保显示最近60秒的数据
        if x_data:
            self.power_controls[key]['power_curve_ax'].set_xlim([x_data[0], x_data[-1]])
        else:
            # 如果没有数据，设置 X 轴范围为默认值
            self.power_controls[key]['power_curve_ax'].set_xlim([0, 60])

        self.power_controls[key]['power_curve_ax'].autoscale()
        self.power_controls[key]['power_curve_ax'].relim()
        self.power_controls[key]['power_curve_ax'].autoscale_view()
        self.power_controls[key]['power_curve_canvas'].draw()


def main():
    app = QApplication(sys.argv)
    ex = PowerSupplyControl()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
