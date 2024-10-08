from PyQt5.QtCore import pyqtSignal, QObject, Qt, QRect, QSize, QRegularExpression, QThread, QProcess, QMetaObject, pyqtSlot
from PyQt5.QtGui import QPainter, QColor, QFont, QTextCursor, QSyntaxHighlighter, QTextCharFormat, QTextFormat
from usb_i2c import USBI2C
from usb_ser import USB_UART
from dmm import DMM34461
from script_thread import ScriptThread
from code_editor import CodeEditor
from python_highlighter import PythonHighlighter
#from power_switch import PowerSupplyControl
from power_switch_function import power_switch_function
import random

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,QSpacerItem, QSizePolicy,
    QPushButton, QPlainTextEdit, QTextEdit, QMessageBox, QFileDialog, QTabWidget,QProgressBar,
    QGridLayout, QFormLayout, QTreeWidget, QTreeWidgetItem, QDialog ,QComboBox 
)

import os
import glob
import tempfile
from enum import Enum

class ScriptButtonState(Enum):
    EXECUTE = 1
    INTERRUPT = 2
    RESUME = 3

class I2CConfigPage(QWidget):
    def __init__(self, devices, global_usb_i2c, global_device_address):
        super().__init__()
        self.usb_i2c = global_usb_i2c
        self.usb_uart = USB_UART()
        self.dmm = DMM34461()
        self.device_address = global_device_address  # Initialize with None
        self.script_thread = None  # Initialize script thread to None
        self.devices = devices
        self.power_switch_function = power_switch_function(self.devices)
        self.script_button_state = ScriptButtonState.EXECUTE
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.register_address_input = QLineEdit(self)
        self.register_address_input.setText("00")
        self.register_address_input.setFixedWidth(50)  # 设置输入框宽度
        self.data_input = QLineEdit(self)
        self.data_input.setText("00")
        self.data_input.setFixedWidth(50)  # 设置输入框宽度
        self.data_input.textChanged.connect(self.update_binary_display)

        self.binary_display = QLineEdit(self)
        self.binary_display.setFixedWidth(80)  # 设置输入框宽度
        self.binary_display.setText("0000_0000")
        self.binary_display.returnPressed.connect(self.update_hex_input)

        address_label = QLabel('寄存器地址:')
        address_label.setFixedWidth(80)  # 设置标签宽度
        data_label = QLabel('数据:')
        data_label.setFixedWidth(40)  # 设置标签宽度
        binary_label = QLabel('二进制:')
        binary_label.setFixedWidth(40)  # 设置标签宽度

        button_layout = QHBoxLayout()
        button_layout.addWidget(address_label)
        button_layout.addWidget(self.register_address_input)
        button_layout.addWidget(data_label)
        button_layout.addWidget(self.data_input)
        button_layout.addWidget(binary_label)
        button_layout.addWidget(self.binary_display)

        self.read_button = QPushButton('读', self)
        self.read_button.clicked.connect(self.read_register)
        button_layout.addWidget(self.read_button)

        self.write_button = QPushButton('写', self)
        self.write_button.clicked.connect(self.write_register)
        button_layout.addWidget(self.write_button)
        button_layout.setAlignment(Qt.AlignLeft)
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        temp_layout = QHBoxLayout()
        self.temperature_label = QLabel('温度: N/A', self)
        temp_layout.addWidget(self.temperature_label)

        self.temperature_progress = QProgressBar(self)
        self.temperature_progress.setRange(-272, 234)  # Range from absolute zero to max temperature
        self.temperature_progress.setTextVisible(False)
        temp_layout.addWidget(self.temperature_progress)

        self.update_temperature_button = QPushButton('更新温度', self)
        self.update_temperature_button.clicked.connect(self.update_temperature)
        temp_layout.addWidget(self.update_temperature_button)
        temp_layout.setAlignment(Qt.AlignLeft)

        self.script_input = CodeEditor(self)
        self.highlighter = PythonHighlighter(self.script_input.document())

        script_button_layout = QHBoxLayout()


        self.load_script_button = QPushButton('加载脚本', self)
        self.load_script_button.clicked.connect(self.load_script)
        script_button_layout.addWidget(self.load_script_button)

        self.save_script_button = QPushButton('保存脚本', self)
        self.save_script_button.clicked.connect(self.save_script)
        script_button_layout.addWidget(self.save_script_button)

        self.clear_script_button = QPushButton('清除脚本', self)
        self.clear_script_button.clicked.connect(self.clear_script)
        script_button_layout.addWidget(self.clear_script_button)

        self.edit_with_vi_button = QPushButton('使用 vi 编辑', self)
        self.edit_with_vi_button.clicked.connect(self.edit_with_vi)
        script_button_layout.addWidget(self.edit_with_vi_button)

        self.script_button = QPushButton('执行脚本', self)
        self.script_button.clicked.connect(self.handle_script_button)
        script_button_layout.addWidget(self.script_button)

        self.exit_button = QPushButton('退出脚本', self)
        self.exit_button.clicked.connect(self.exit_script)
        self.exit_button.setEnabled(False)
        script_button_layout.addWidget(self.exit_button)

        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(True)
        self.result_output.setAcceptRichText(True)

        result_button_layout = QHBoxLayout()
        self.save_output_button = QPushButton('保存输出结果', self)
        self.save_output_button.clicked.connect(self.save_output)
        result_button_layout.addWidget(self.save_output_button)

        self.clear_output_button = QPushButton('清除输出结果', self)
        self.clear_output_button.clicked.connect(self.clear_output)
        result_button_layout.addWidget(self.clear_output_button)

        self.status_label = QLabel('脚本状态: 空闲', self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("background-color: yellow;")

        self.script_path_label = QLabel('Python 脚本: 未加载', self)
        self.script_path_label.setAlignment(Qt.AlignLeft)

        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        layout.addLayout(temp_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.script_path_label)
        layout.addWidget(self.script_input)
        layout.addLayout(script_button_layout)
        layout.addWidget(QLabel('执行结果:'))
        layout.addWidget(self.result_output)
        layout.addWidget(QLabel('二进制数据编辑完成后，请按回车键确认。'))
        layout.addLayout(result_button_layout)

        self.setLayout(layout)

    def handle_script_button(self):
        if self.script_button_state == ScriptButtonState.EXECUTE:
            self.execute_script()
        elif self.script_button_state == ScriptButtonState.INTERRUPT:
            self.interrupt_script()
        elif self.script_button_state == ScriptButtonState.RESUME:
            self.resume_script()

    # def execute_script(self):
    #     script = self.script_input.toPlainText()
    #     self.script_thread = ScriptThread(script, self.read_i2c, self.write_i2c, self.power_switch_function,self.read_uart,self.write_uart, self.read_i2c_disp,self.write_i2c_disp)
    #     self.script_thread.output.connect(self.append_output)
    #     self.script_thread.finished.connect(self.on_script_finished)
    #     self.script_thread.paused.connect(self.on_script_paused)
    #     self.script_thread.resumed.connect(self.on_script_resumed)
    #     self.script_thread.start()

    #     self.script_button_state = ScriptButtonState.INTERRUPT
    #     self.script_button.setText('中断脚本')
    #     self.status_label.setText('脚本状态: 运行中')
    #     self.status_label.setStyleSheet("background-color: rgb(144, 238, 144);")
    #     self.exit_button.setEnabled(True)


    def execute_script(self):
        script = self.script_input.toPlainText()
        self.script_thread = ScriptThread(script, self.read_i2c, self.write_i2c, self.power_switch_function,self.dmm, self.read_uart, self.write_uart, self.read_i2c_disp, self.write_i2c_disp)
        self.script_thread.output.connect(self.append_output)
        self.script_thread.finished.connect(self.on_script_finished)
        self.script_thread.paused.connect(self.on_script_paused)
        self.script_thread.resumed.connect(self.on_script_resumed)
        self.script_thread.start()

        # 使用 QMetaObject.invokeMethod 将 UI 更新操作调度到主线程
        QMetaObject.invokeMethod(self, "update_ui_for_script_running", Qt.QueuedConnection)
    @pyqtSlot()
    def update_ui_for_script_running(self):
        self.script_button_state = ScriptButtonState.INTERRUPT
        self.script_button.setText('中断脚本')
        self.status_label.setText('脚本状态: 运行中')
        self.status_label.setStyleSheet("background-color: rgb(144, 238, 144);")
        self.exit_button.setEnabled(True)


    def interrupt_script(self):
        if self.script_thread and self.script_thread.isRunning():
            self.script_thread.interrupt()
            self.append_output("脚本执行被中断\n")
            self.script_button_state = ScriptButtonState.RESUME
            self.script_button.setText('恢复执行')

    def resume_script(self):
        if self.script_thread and self.script_thread.isRunning():
            self.script_thread.resume()
            self.append_output("脚本执行已恢复。\n")
            self.script_button_state = ScriptButtonState.INTERRUPT
            self.script_button.setText('中断脚本')

    def on_script_finished(self):
        self.status_label.setText('脚本状态: 空闲')
        self.status_label.setStyleSheet("background-color: yellow;")
        self.script_button_state = ScriptButtonState.EXECUTE
        self.script_button.setText('执行脚本')
        self.exit_button.setEnabled(False)

    def on_script_paused(self):
        self.status_label.setText('脚本状态: 已暂停')
        self.status_label.setStyleSheet("background-color: orange;")
        self.script_button_state = ScriptButtonState.RESUME
        self.script_button.setText('恢复执行')

    def on_script_resumed(self):
        self.status_label.setText('脚本状态: 运行中')
        self.status_label.setStyleSheet("background-color: green;")
        self.script_button_state = ScriptButtonState.INTERRUPT
        self.script_button.setText('中断脚本')

    def exit_script(self):
        if self.script_thread and self.script_thread.isRunning():
            self.script_thread.exit()
            self.append_output("正在终止脚本执行...\n")
            self.exit_button.setEnabled(False)

    def update_binary_display(self):
        try:
            hex_value = int(self.data_input.text(), 16)
            binary_value = f"{hex_value:08b}".replace("0", "0").replace("1", "1")
            binary_value = f"{binary_value[:4]}_{binary_value[4:]}"
            self.binary_display.setText(binary_value)
        except ValueError:
            self.binary_display.setText("0000_0000")

    def update_hex_input(self):
        try:
            binary_text = self.binary_display.text().replace("_", "")
            if len(binary_text) != 8 or not all(c in "01" for c in binary_text):
                raise ValueError("Invalid binary format")
            hex_value = hex(int(binary_text, 2))[2:].upper().zfill(2)
            self.data_input.setText(hex_value)
        except ValueError:
            self.data_input.setText("00")

    def update_device_address(self, new_address=None):
        if new_address is None:
            try:
                new_address = int(self.device_address_input.text(), 16)
            except ValueError:
                QMessageBox.critical(self, '错误', '无效的设备地址')
                return
        
        self.device_address = new_address
        self.device_address_input.setText(f"0x{new_address:02X}")
        self.usb_i2c.update_device_address(new_address)
        print(f'设备地址更新为: 0x{new_address:02X}')

    def clear_script(self):
        self.script_input.clear()
        self.script_path_label.setText('Python 脚本: 未加载')

    def save_output(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "保存输出结果", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.result_output.toPlainText())

    def clear_output(self):
        self.result_output.clear()

    def read_register(self):
        if self.device_address is None:
            QMessageBox.critical(self, '错误', '请先更新设备地址')
            return
        try:
            register_address = int(self.register_address_input.text(), 16)
            data = self.usb_i2c.read(register_address)
            self.data_input.setText(f'{data:02X}')
            self.append_output(f'读取 0x{register_address:02X}: 0x{data:02X}\n')
        except ValueError:
            QMessageBox.critical(self, '错误', '无效的寄存器地址')

    def write_register(self):
        if self.device_address is None:
            QMessageBox.critical(self, '错误', '请先更新设备地址')
            return
        try:
            register_address = int(self.register_address_input.text(), 16)
            data = int(self.data_input.text(), 16)
            self.usb_i2c.write(register_address, data)
            self.append_output(f'写入 0x{register_address:02X}: 0x{data:02X}\n')
        except ValueError:
            QMessageBox.critical(self, '错误', '无效的寄存器地址或数据')
    
    # def write_uart(self,hex_string):
    #     try:
    #         self.usb_uart.uart_write(hex_string)
    #     except ValueError:
    #         QMessageBox.critical(self, '错误', '无法配置UART')
    # def read_uart(self,timeout=1, num_bytes=1024):
    #     try:
    #         self.usb_uart.uart_read(timeout=1, num_bytes=1024)
    #     except ValueError:
    #         QMessageBox.critical(self, '错误', '无法读取UART')
    
    # def read_uart(self, timeout=1, num_bytes=1024):
    #     try:
    #         data = self.usb_uart.uart_read(timeout=timeout, num_bytes=num_bytes)
    #         if data is None:
    #             QMessageBox.warning(self, '警告', '未接收到数据')
    #         return data
    #     except Exception as e:
    #         QMessageBox.critical(self, '错误', f'读取UART时发生错误: {str(e)}')
    #         return None

    def append_output(self, text):
        self.result_output.moveCursor(QTextCursor.End)
        self.result_output.insertHtml(text + "<br>")
        self.result_output.moveCursor(QTextCursor.End)

    def read_i2c(self, register_address):
        if self.device_address is None:
            raise ValueError('设备地址未设置')
        return self.usb_i2c.read(register_address)

    def write_i2c(self, register_address, data):
        if self.device_address is None:
            raise ValueError('设备地址未设置')
        self.usb_i2c.write(register_address, data)

    def read_i2c_disp(self,register_address):
        if self.device_address is None:
            QMessageBox.critical(self, '错误', '请先更新设备地址')
            return
        try:
            data = self.usb_i2c.read(register_address)
            self.append_output(f'读取 0x{register_address:02X}: 0x{data:02X}\n')
        except ValueError:
            QMessageBox.critical(self, '错误', '无效的寄存器地址')

    def write_i2c_disp(self,register_address,data):
        if self.device_address is None:
            QMessageBox.critical(self, '错误', '请先更新设备地址')
            return
        try:
            self.usb_i2c.write(register_address, data)
            self.append_output(f'写入 0x{register_address:02X}: 0x{data:02X}\n')
        except ValueError:
            QMessageBox.critical(self, '错误', '无效的寄存器地址或数据')
    
    def write_uart(self,hex_string):
        try:
            rd_hex = self.usb_uart.uart_write(hex_string)
            self.append_output(f"UART 写入: {hex_string}\n")
            self.append_output(f"UART 返回: {rd_hex}\n")
            return rd_hex
        except ValueError:
            QMessageBox.critical(self, '错误', '无法配置UART')
            return None

    def read_uart(self, timeout=1, num_bytes=1024):
        try:
            data = self.usb_uart.uart_read(timeout=timeout, num_bytes=num_bytes)
            if data is None:
                #QMessageBox.warning(self, '警告', '未接收到数据')
                self.append_output(f'警告 :未接收到数据')
            else:
                #hex_data = ' '.join([f'{byte:02X}' for byte in data])
                #print(f"接收到的十六进制数据: {hex_data}")
                self.append_output(f'接收到的十六进制数据: {data}\n')

            return data
        except Exception as e:
            QMessageBox.critical(self, '错误', f'读取UART时发生错误: {str(e)}')
            return None

    def append_output(self, text):
        self.result_output.moveCursor(QTextCursor.End)
        self.result_output.insertHtml(text + "<br>")
        self.result_output.moveCursor(QTextCursor.End)

    def read_i2c(self, register_address):
        if self.device_address is None:
            raise ValueError('设备地址未设置')
        return self.usb_i2c.read(register_address)

    def write_i2c(self, register_address, data):
        if self.device_address is None:
            raise ValueError('设备地址未设置')
        self.usb_i2c.write(register_address, data)

    def load_script(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "加载脚本", "", "Python Files (*.py);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'r') as file:
                self.script_input.setPlainText(file.read())
            self.script_path_label.setText(f'Python 脚本: {file_name}')

    def save_script(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "保存脚本", "", "Python Files (*.py);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.script_input.toPlainText())

    def find_gvim(self):
        possible_patterns = [
            r'C:\Program Files (x86)\Vim\vim*\gvim.exe',
            r'C:\Program Files\Vim\vim*\gvim.exe',
            r'D:\Program Files (x86)\Vim\vim*\gvim.exe',
            r'D:\Program Files\Vim\vim*\gvim.exe',
            r'E:\Program Files (x86)\Vim\vim*\gvim.exe',
            r'E:\Program Files\Vim\vim*\gvim.exe' 
        ]

        for pattern in possible_patterns:
            for path in glob.glob(pattern):
                if os.path.isfile(path):
                    return path
        return None

    def edit_with_vi(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.py')
        temp_file_name = temp_file.name
        temp_file.close()
        gvim_location = self.find_gvim()

        try:
            with open(temp_file_name, 'w') as file:
                file.write(self.script_input.toPlainText())
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法写入临时文件: {str(e)}')
            return

        process = QProcess(self)
        process.finished.connect(lambda exit_code, exit_status: self.on_vi_finished(temp_file_name, exit_code, exit_status))
        process.start(gvim_location, ['-f', temp_file_name])

    def on_vi_finished(self, temp_file_name, exit_code, exit_status):
        if exit_code != 0:
            QMessageBox.critical(self, '错误', f'vi 编辑器退出代码: {exit_code}')
            return

        try:
            with open(temp_file_name, 'r') as file:
                script = file.read()
                self.script_input.setPlainText(script)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法读取临时文件: {str(e)}')

        try:
            os.remove(temp_file_name)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法删除临时文件: {str(e)}')
    
    def update_temperature(self):
        try:
            register_address = 0xE0
            data = self.usb_i2c.read(register_address)
            temperature = (data / 255.0) * 505.78 - 272
            self.temperature_label.setText(f'温度: <b> {temperature:.1f} </b>°C')
            self.temperature_progress.setValue(int(temperature))
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法读取温度: {str(e)}')


    def load_script(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "加载脚本", "", "Python Files (*.py);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'r') as file:
                self.script_input.setPlainText(file.read())
            self.script_path_label.setText(f'Python 脚本: {file_name}')

    def save_script(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "保存脚本", "", "Python Files (*.py);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.script_input.toPlainText())

    def find_gvim(self):
        possible_patterns = [
            r'C:\Program Files (x86)\Vim\vim*\gvim.exe',
            r'C:\Program Files\Vim\vim*\gvim.exe',
            r'D:\Program Files (x86)\Vim\vim*\gvim.exe',
            r'D:\Program Files\Vim\vim*\gvim.exe',
            r'E:\Program Files (x86)\Vim\vim*\gvim.exe',
            r'E:\Program Files\Vim\vim*\gvim.exe' 
        ]

        for pattern in possible_patterns:
            for path in glob.glob(pattern):
                if os.path.isfile(path):
                    return path
        return None

    def edit_with_vi(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.py')
        temp_file_name = temp_file.name
        temp_file.close()
        gvim_location = self.find_gvim()

        try:
            with open(temp_file_name, 'w') as file:
                file.write(self.script_input.toPlainText())
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法写入临时文件: {str(e)}')
            return

        process = QProcess(self)
        process.finished.connect(lambda exit_code, exit_status: self.on_vi_finished(temp_file_name, exit_code, exit_status))
        process.start(gvim_location, ['-f', temp_file_name])

    def on_vi_finished(self, temp_file_name, exit_code, exit_status):
        if exit_code != 0:
            QMessageBox.critical(self, '错误', f'vi 编辑器退出代码: {exit_code}')
            return

        try:
            with open(temp_file_name, 'r') as file:
                script = file.read()
                self.script_input.setPlainText(script)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法读取临时文件: {str(e)}')

        try:
            os.remove(temp_file_name)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法删除临时文件: {str(e)}')
    
    def update_temperature(self):
        try:
            register_address = 0xE0
            data = self.usb_i2c.read(register_address)
            temperature = (data / 255.0) * 505.78 - 272
            self.temperature_label.setText(f'温度: <b> {temperature:.1f} </b>°C')
            self.temperature_progress.setValue(int(temperature))
            self.set_progress_bar_style(temperature)
            self.append_output(f'温度读取自寄存器 0x{register_address:02X}: {temperature:.1f} °C\n')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'读取温度时出错: {str(e)}')

    def set_progress_bar_style(self, temperature):
        temperature = max(-272, min(temperature, 233.78))
        normalized_temp = (temperature + 272) / 505.78
        red = int(255 * normalized_temp)
        green = 0
        blue = int(255 * (1 - normalized_temp))
        color = f'rgb({red}, {green}, {blue})'
        self.temperature_progress.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")
####################################################################################################################################################################