# from PyQt5.QtCore import pyqtSignal, QObject, Qt, QRect, QSize, QRegularExpression, QThread, QProcess
# from PyQt5.QtGui import QPainter, QColor, QFont, QTextCursor, QSyntaxHighlighter, QTextCharFormat, QTextFormat
# from usb_i2c import USBI2C
# from usb_ser import USB_UART
# from script_thread import ScriptThread
# from code_editor import CodeEditor
# from python_highlighter import PythonHighlighter
# #from power_switch import PowerSupplyControl
# from power_switch_function import power_switch_function
# import random

# from PyQt5.QtWidgets import (
#     QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,QSpacerItem, QSizePolicy,
#     QPushButton, QPlainTextEdit, QTextEdit, QMessageBox, QFileDialog, QTabWidget,QProgressBar,
#     QGridLayout, QFormLayout, QTreeWidget, QTreeWidgetItem, QDialog ,QComboBox 
# )

# import os
# import glob
# import tempfile


# class I2CConfigPage(QWidget):
#     def __init__(self,devices,global_usb_i2c,global_device_address):
#         super().__init__()
#         self.usb_i2c = global_usb_i2c
#         self.usb_uart = USB_UART()
#         self.device_address = global_device_address  # Initialize with None
#         self.script_thread = None  # Initialize script thread to None
#         self.devices = devices
#         #self.power_supply_control = PowerSupplyControl
#         self.power_switch_function = power_switch_function(self.devices)
#         self.init_ui()

#     def init_ui(self):
#         layout = QVBoxLayout()
#         form_layout = QFormLayout()

#         # Device address input and update button
#         # self.device_address_input = QLineEdit(self)
#         # self.device_address_input.setText(f"0x{self.device_address:02X}")
#         # self.device_address_input.setFixedWidth(50)
        
#         # update_address_button = QPushButton('更新设备地址', self)
#         # update_address_button.clicked.connect(self.update_device_address)

#         # device_address_layout = QHBoxLayout()
#         # device_address_layout.addWidget(self.device_address_input)
#         # device_address_layout.addWidget(update_address_button)
#         # device_address_layout.setAlignment(Qt.AlignLeft)
#         # device_address_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
#         # # Add the device address row to the form layout
#         # form_layout.addRow(QLabel('设备地址:'), device_address_layout)
        
#         self.register_address_input = QLineEdit(self)
#         self.register_address_input.setText("00")
#         self.register_address_input.setFixedWidth(50)  # 设置输入框宽度
#         self.data_input = QLineEdit(self)
#         self.data_input.setText("00")
#         self.data_input.setFixedWidth(50)  # 设置输入框宽度
#         self.binary_display = QLineEdit(self)
#         self.binary_display.setFixedWidth(80)  # 设置输入框宽度
#         self.binary_display.setText("0000_0000")
#         self.binary_display.textChanged.connect(self.update_hex_input)

#         address_label = QLabel('寄存器地址:')
#         address_label.setFixedWidth(80)  # 设置标签宽度
#         data_label = QLabel('数据:')
#         data_label.setFixedWidth(40)  # 设置标签宽度
#         binary_label = QLabel('二进制:')
#         binary_label.setFixedWidth(40)  # 设置标签宽度

#         button_layout = QHBoxLayout()
#         button_layout.addWidget(address_label)
#         button_layout.addWidget(self.register_address_input)
#         button_layout.addWidget(data_label)
#         button_layout.addWidget(self.data_input)

#         self.read_button = QPushButton('读', self)
#         self.read_button.clicked.connect(self.read_register)
#         #button_layout.addWidget(self.read_button)
#         button_layout.addWidget(self.read_button)

#         self.write_button = QPushButton('写', self)
#         self.write_button.clicked.connect(self.write_register)
#         #button_layout.addWidget(self.write_button)
#         button_layout.addWidget(self.write_button)
#         button_layout.setAlignment(Qt.AlignLeft)
#         button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))


#         temp_layout = QHBoxLayout()
#          # Add temperature label
#         self.temperature_label = QLabel('温度: N/A', self)
#         #temp_layout.addWidget(QLabel('温度:'))
#         temp_layout.addWidget(self.temperature_label)

#          # Add a progress bar to show temperature
#         self.temperature_progress = QProgressBar(self)
#         self.temperature_progress.setRange(-272, 234)  # Range from absolute zero to max temperature
#         self.temperature_progress.setTextVisible(False)
#         temp_layout.addWidget(self.temperature_progress)

#         # Add a button to update the temperature
#         self.update_temperature_button = QPushButton('更新温度', self)
#         self.update_temperature_button.clicked.connect(self.update_temperature)
#         #form_layout.addRow(self.update_temperature_button)
#         temp_layout.addWidget(self.update_temperature_button)
#         temp_layout.setAlignment(Qt.AlignLeft)

#         self.script_input = CodeEditor(self)
#         self.highlighter = PythonHighlighter(self.script_input.document())

#         script_button_layout = QHBoxLayout()
#         self.load_script_button = QPushButton('加载脚本', self)
#         self.load_script_button.clicked.connect(self.load_script)
#         script_button_layout.addWidget(self.load_script_button)

#         self.save_script_button = QPushButton('保存脚本', self)
#         self.save_script_button.clicked.connect(self.save_script)
#         script_button_layout.addWidget(self.save_script_button)

        

#         self.clear_script_button = QPushButton('清除脚本', self)
#         self.clear_script_button.clicked.connect(self.clear_script)
#         script_button_layout.addWidget(self.clear_script_button)

#         self.edit_with_vi_button = QPushButton('使用 vi 编辑', self)
#         self.edit_with_vi_button.clicked.connect(self.edit_with_vi)
#         script_button_layout.addWidget(self.edit_with_vi_button)

#         self.execute_button = QPushButton('执行脚本', self)
#         self.execute_button.clicked.connect(self.execute_script)
#         script_button_layout.addWidget(self.execute_button)
#         #button_layout.addWidget(self.execute_button)

#         # Add a new button for interrupting script execution
#         self.interrupt_button = QPushButton('中断脚本', self)
#         self.interrupt_button.clicked.connect(self.interrupt_script)
#         self.interrupt_button.setEnabled(False)  # Disabled by default
#         script_button_layout.addWidget(self.interrupt_button)
#         #button_layout.addWidget(self.interrupt_button)

#         self.resume_button = QPushButton('恢复执行', self)
#         self.resume_button.clicked.connect(self.resume_script)
#         self.resume_button.setEnabled(False)
#         script_button_layout.addWidget(self.resume_button)

#         self.exit_button = QPushButton('退出脚本', self)
#         self.exit_button.clicked.connect(self.exit_script)
#         self.exit_button.setEnabled(False)
#         script_button_layout.addWidget(self.exit_button)

#         self.result_output = QTextEdit(self)
#         # self.result_output.setReadOnly(True)
#         #self.result_output = ANSIConsole(self)
#         self.result_output.setReadOnly(True)
#         self.result_output.setAcceptRichText(True)

#         result_button_layout = QHBoxLayout()
#         self.save_output_button = QPushButton('保存输出结果', self)
#         self.save_output_button.clicked.connect(self.save_output)
#         result_button_layout.addWidget(self.save_output_button)

#         self.clear_output_button = QPushButton('清除输出结果', self)
#         self.clear_output_button.clicked.connect(self.clear_output)
#         result_button_layout.addWidget(self.clear_output_button)

#         # Status indicator
#         self.status_label = QLabel('脚本状态: 空闲', self)
#         self.status_label.setAlignment(Qt.AlignCenter)
#         self.status_label.setStyleSheet("background-color: yellow;")

#          # 创建一个 QWidget 作为容器，并设置样式表
#         #layout_container = QWidget()
#         #layout_container.setLayout(temp_layout)
#         #layout_container.setStyleSheet("border: 1px solid black;")  # 设置边界线
#         self.script_path_label = QLabel('Python 脚本: 未加载', self)
#         self.script_path_label.setAlignment(Qt.AlignLeft)

#         layout.addLayout(form_layout)
#         layout.addLayout(button_layout)
#         layout.addLayout(temp_layout)
#         #layout.addWidget(layout_container)
#         layout.addWidget(self.status_label)
#         layout.addWidget(self.script_path_label)
#         layout.addWidget(self.script_input)
#         layout.addLayout(script_button_layout)
#         layout.addWidget(QLabel('执行结果:'))
#         layout.addWidget(self.result_output)
#         layout.addLayout(result_button_layout)

#         self.setLayout(layout)
#     def update_device_address(self, new_address=None):
#         if new_address is None:
#             try:
#                 new_address = int(self.device_address_input.text(), 16)
#             except ValueError:
#                 QMessageBox.critical(self, '错误', '无效的设备地址')
#                 return
        
#         self.device_address = new_address
#         self.device_address_input.setText(f"0x{new_address:02X}")
#         self.usb_i2c.update_device_address(new_address)
#         print(f'设备地址更新为: 0x{new_address:02X}')


#     def clear_script(self):
#         self.script_input.clear()
#         self.script_path_label.setText('Python 脚本: 未加载')

#     def update_binary_display(self):
#         try:
#             hex_value = int(self.data_input.text(), 16)
#             binary_value = f"{hex_value:08b}".replace("0", "0").replace("1", "1")
#             binary_value = f"{binary_value[:4]}_{binary_value[4:]}"
#             self.binary_display.setText(binary_value)
#         except ValueError:
#             self.binary_display.setText("0000_0000")

#     def update_hex_input(self):
#         try:
#             binary_text = self.binary_display.text().replace("_", "")
#             if len(binary_text) != 8 or not all(c in "01" for c in binary_text):
#                 raise ValueError("Invalid binary format")
#             hex_value = hex(int(binary_text, 2))[2:].upper().zfill(2)
#             self.data_input.setText(hex_value)
#         except ValueError:
#             self.data_input.setText("00")

#     def save_output(self):
#         options = QFileDialog.Options()
#         file_name, _ = QFileDialog.getSaveFileName(self, "保存输出结果", "", "Text Files (*.txt);;All Files (*)", options=options)
#         if file_name:
#             with open(file_name, 'w') as file:
#                 file.write(self.result_output.toPlainText())

#     def clear_output(self):
#         self.result_output.clear()

#     def read_register(self):
#         if self.device_address is None:
#             QMessageBox.critical(self, '错误', '请先更新设备地址')
#             return
#         try:
#             register_address = int(self.register_address_input.text(), 16)
#             data = self.usb_i2c.read(register_address)
#             self.data_input.setText(f'{data:02X}')
#             self.append_output(f'读取 0x{register_address:02X}: 0x{data:02X}\n')
#         except ValueError:
#             QMessageBox.critical(self, '错误', '无效的寄存器地址')

#     def write_register(self):
#         if self.device_address is None:
#             QMessageBox.critical(self, '错误', '请先更新设备地址')
#             return
#         try:
#             register_address = int(self.register_address_input.text(), 16)
#             data = int(self.data_input.text(), 16)
#             self.usb_i2c.write(register_address, data)
#             self.append_output(f'写入 0x{register_address:02X}: 0x{data:02X}\n')
#         except ValueError:
#             QMessageBox.critical(self, '错误', '无效的寄存器地址或数据')
    
#     def write_uart(self,hex_string):
#         try:
#             self.usb_uart.uart_write(hex_string)
#         except ValueError:
#             QMessageBox.critical(self, '错误', '无法配置UART')

#     # def append_output(self, text):
#     #     self.result_output.moveCursor(QTextCursor.End)
#     #     self.result_output.insertPlainText(text)
#     #     self.result_output.moveCursor(QTextCursor.End)

#     def append_output(self, text):
#         self.result_output.moveCursor(QTextCursor.End)
#         self.result_output.insertHtml(text + "<br>")
#         self.result_output.moveCursor(QTextCursor.End)

#     def execute_script(self):
#         script = self.script_input.toPlainText()
#         self.script_thread = ScriptThread(script, self.read_i2c, self.write_i2c, self.write_uart, self.power_switch_function)
#         self.script_thread.output.connect(self.append_output)
#         self.script_thread.finished.connect(self.on_script_finished)
#         self.script_thread.paused.connect(self.on_script_paused)
#         self.script_thread.resumed.connect(self.on_script_resumed)
#         self.script_thread.start()

#         self.execute_button.setEnabled(False)
#         self.interrupt_button.setEnabled(True)
#         self.resume_button.setEnabled(False)
#         self.exit_button.setEnabled(True)
#         self.status_label.setText('脚本状态: 运行中')
#         self.status_label.setStyleSheet("background-color: rgb(144, 238, 144);")

    


#     def interrupt_script(self):
#         if self.script_thread and self.script_thread.isRunning():
#             self.script_thread.interrupt()
#             self.append_output("脚本执行被中断\n")

#     def resume_script(self):
#         if self.script_thread and self.script_thread.isRunning():
#             self.script_thread.resume()
#             self.append_output("脚本执行已恢复。\n")
#             self.resume_button.setEnabled(False)
#             self.interrupt_button.setEnabled(True)

#     def exit_script(self):
#         if self.script_thread and self.script_thread.isRunning():
#             self.script_thread.exit()
#             self.append_output("正在终止脚本执行...\n")

#     def on_script_finished(self):
#         self.status_label.setText('脚本状态: 空闲')
#         self.status_label.setStyleSheet("background-color: yellow;")
#         self.execute_button.setEnabled(True)
#         self.interrupt_button.setEnabled(False)
#         self.resume_button.setEnabled(False)
#         self.exit_button.setEnabled(False)
#         self.append_output("脚本执行已完成。\n")

#     def on_script_paused(self):
#         self.status_label.setText('脚本状态: 已暂停')
#         self.status_label.setStyleSheet("background-color: orange;")
#         self.interrupt_button.setEnabled(False)
#         self.resume_button.setEnabled(True)
#         self.append_output("脚本执行已暂停\n")

#     def on_script_resumed(self):
#         self.status_label.setText('脚本状态: 运行中')
#         self.status_label.setStyleSheet("background-color: green;")
#         self.interrupt_button.setEnabled(True)
#         self.resume_button.setEnabled(False)
#         self.append_output("脚本执行已恢复\n")

#     def on_interrupt_occurred(self):
#         self.interrupt_button.setEnabled(False)
#         self.resume_button.setEnabled(True)
#         self.exit_button.setEnabled(True)

#     def read_i2c(self, register_address):
#         if self.device_address is None:
#             raise ValueError('设备地址未设置')
#         #return self.usb_i2c.read_register(self.device_address, register_address)
#         return self.usb_i2c.read(register_address)

#     def write_i2c(self, register_address, data):
#         if self.device_address is None:
#             raise ValueError('设备地址未设置')
#         #self.usb_i2c.write_register(self.device_address, register_address, data)
#         self.usb_i2c.write(register_address, data)

#     # def load_script(self):
#     #     options = QFileDialog.Options()
#     #     file_name, _ = QFileDialog.getOpenFileName(self, "加载脚本", "", "Python Files (*.py);;All Files (*)", options=options)
#     #     if file_name:
#     #         with open(file_name, 'r') as file:
#     #             self.script_input.setPlainText(file.read())
    
#     def load_script(self):
#         options = QFileDialog.Options()
#         file_name, _ = QFileDialog.getOpenFileName(self, "加载脚本", "", "Python Files (*.py);;All Files (*)", options=options)
#         if file_name:
#             with open(file_name, 'r') as file:
#                 self.script_input.setPlainText(file.read())
#             self.script_path_label.setText(f'Python 脚本: {file_name}')

#     def save_script(self):
#         options = QFileDialog.Options()
#         file_name, _ = QFileDialog.getSaveFileName(self, "保存脚本", "", "Python Files (*.py);;All Files (*)", options=options)
#         if file_name:
#             with open(file_name, 'w') as file:
#                 file.write(self.script_input.toPlainText())



#     def find_gvim(self):
#         # 使用通配符查找所有可能的 gvim.exe 路径
#         possible_patterns = [
#             r'C:\Program Files (x86)\Vim\vim*\gvim.exe',
#             r'C:\Program Files\Vim\vim*\gvim.exe',
#             r'D:\Program Files (x86)\Vim\vim*\gvim.exe',
#             r'D:\Program Files\Vim\vim*\gvim.exe',
#             r'E:\Program Files (x86)\Vim\vim*\gvim.exe',
#             r'E:\Program Files\Vim\vim*\gvim.exe' 
#         ]

#         for pattern in possible_patterns:
#             # 使用 glob 模块查找匹配的路径
#             for path in glob.glob(pattern):
#                 if os.path.isfile(path):
#                     return path
#         return None


#     def edit_with_vi(self):
#         # Create a temporary file
#         temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.py')
#         temp_file_name = temp_file.name
#         temp_file.close()
#         gvim_location = self.find_gvim()

#         # Save current script content to the temporary file
#         try:
#             with open(temp_file_name, 'w') as file:
#                 file.write(self.script_input.toPlainText())
#         except Exception as e:
#             QMessageBox.critical(self, '错误', f'无法写入临时文件: {str(e)}')
#             return

#         # Start the external editor (vi)
#         process = QProcess(self)
#         process.finished.connect(lambda exit_code, exit_status: self.on_vi_finished(temp_file_name, exit_code, exit_status))
#         #process.start('C:/Program Files \\(x86\\)/Vim/vim82/gvim.exe', ['-f' temp_file_name])
#         #process.start('C:\\Program Files (x86)\\Vim\\vim82\\gvim.exe', ['-f', temp_file_name])
#         process.start(gvim_location, ['-f', temp_file_name])

#     def on_vi_finished(self, temp_file_name, exit_code, exit_status):
#         if exit_code != 0:
#             QMessageBox.critical(self, '错误', f'vi 编辑器退出代码: {exit_code}')
#             return

#         # Read the content of the temporary file back to the script input
#         try:
#             with open(temp_file_name, 'r') as file:
#                 script = file.read()
#                 self.script_input.setPlainText(script)
#         except Exception as e:
#             QMessageBox.critical(self, '错误', f'无法读取临时文件: {str(e)}')

#         # Remove the temporary file
#         try:
#             os.remove(temp_file_name)
#         except Exception as e:
#             QMessageBox.critical(self, '错误', f'无法删除临时文件: {str(e)}')
    

#     # def update_temperature(self):
#     #     try:
#     #         register_address = 0xE0
#     #         data = self.usb_i2c.read(register_address)
#     #         temperature = (data / 255.0)* 505.78  - 272
#     #         self.temperature_label.setText(f'温度: <b> {temperature:.1f} </b>°C')
#     #         self.append_output(f'温度读取自寄存器 0x{register_address:02X}: {temperature:.1f} °C\n')
#     #     except Exception as e:
#     #         QMessageBox.critical(self, '错误', f'读取温度时出错: {str(e)}')

#     def update_temperature(self):
#         try:
#             register_address = 0xE0
#             data = self.usb_i2c.read(register_address)
#             #data = random.randint(0,255)
#             temperature = (data / 255.0) * 505.78 - 272
#             self.temperature_label.setText(f'温度: <b> {temperature:.1f} </b>°C')
#             self.temperature_progress.setValue(int(temperature))
#             self.set_progress_bar_style(temperature)
#             self.append_output(f'温度读取自寄存器 0x{register_address:02X}: {temperature:.1f} °C\n')
#         except Exception as e:
#             QMessageBox.critical(self, '错误', f'读取温度时出错: {str(e)}')

#     # def set_progress_bar_style(self, temperature):
#     #     # Calculate color based on temperature
#     #     red = int(255 * (temperature + 272) / 505.78)
#     #     green = int(255 * (1 - (temperature + 272) / 505.78))
#     #     blue = 0
#     #     color = f'rgb({red}, {green}, {blue})'
#     #     self.temperature_progress.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")
#     def set_progress_bar_style(self, temperature):
#         # Calculate color based on temperature
#         temperature = max(-272, min(temperature, 233.78))  # Clamp temperature to valid range
#         normalized_temp = (temperature + 272) / 505.78
#         red = int(255 * normalized_temp)
#         green = 0
#         blue = int(255 * (1 - normalized_temp))
#         color = f'rgb({red}, {green}, {blue})'
#         self.temperature_progress.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")

####################################################################################################################################################################
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QRect, QSize, QRegularExpression, QThread, QProcess
from PyQt5.QtGui import QPainter, QColor, QFont, QTextCursor, QSyntaxHighlighter, QTextCharFormat, QTextFormat
from usb_i2c import USBI2C
from usb_ser import USB_UART
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


class I2CConfigPage(QWidget):
    def __init__(self,devices,global_usb_i2c,global_device_address):
        super().__init__()
        self.usb_i2c = global_usb_i2c
        self.usb_uart = USB_UART()
        self.device_address = global_device_address  # Initialize with None
        self.script_thread = None  # Initialize script thread to None
        self.devices = devices
        #self.power_supply_control = PowerSupplyControl
        self.power_switch_function = power_switch_function(self.devices)
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

        self.execute_button = QPushButton('执行脚本', self)
        self.execute_button.clicked.connect(self.execute_script)
        script_button_layout.addWidget(self.execute_button)

        self.interrupt_button = QPushButton('中断脚本', self)
        self.interrupt_button.clicked.connect(self.interrupt_script)
        self.interrupt_button.setEnabled(False)  # Disabled by default
        script_button_layout.addWidget(self.interrupt_button)

        self.resume_button = QPushButton('恢复执行', self)
        self.resume_button.clicked.connect(self.resume_script)
        self.resume_button.setEnabled(False)
        script_button_layout.addWidget(self.resume_button)

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
    
    def write_uart(self,hex_string):
        try:
            self.usb_uart.uart_write(hex_string)
        except ValueError:
            QMessageBox.critical(self, '错误', '无法配置UART')

    def append_output(self, text):
        self.result_output.moveCursor(QTextCursor.End)
        self.result_output.insertHtml(text + "<br>")
        self.result_output.moveCursor(QTextCursor.End)

    def execute_script(self):
        script = self.script_input.toPlainText()
        self.script_thread = ScriptThread(script, self.read_i2c, self.write_i2c, self.write_uart, self.power_switch_function)
        self.script_thread.output.connect(self.append_output)
        self.script_thread.finished.connect(self.on_script_finished)
        self.script_thread.paused.connect(self.on_script_paused)
        self.script_thread.resumed.connect(self.on_script_resumed)
        self.script_thread.start()

        self.execute_button.setEnabled(False)
        self.interrupt_button.setEnabled(True)
        self.resume_button.setEnabled(False)
        self.exit_button.setEnabled(True)
        self.status_label.setText('脚本状态: 运行中')
        self.status_label.setStyleSheet("background-color: rgb(144, 238, 144);")

    def interrupt_script(self):
        if self.script_thread and self.script_thread.isRunning():
            self.script_thread.interrupt()
            self.append_output("脚本执行被中断\n")

    def resume_script(self):
        if self.script_thread and self.script_thread.isRunning():
            self.script_thread.resume()
            self.append_output("脚本执行已恢复。\n")
            self.resume_button.setEnabled(False)
            self.interrupt_button.setEnabled(True)

    def exit_script(self):
        if self.script_thread and self.script_thread.isRunning():
            self.script_thread.exit()
            self.append_output("正在终止脚本执行...\n")

    def on_script_finished(self):
        self.status_label.setText('脚本状态: 空闲')
        self.status_label.setStyleSheet("background-color: yellow;")
        self.execute_button.setEnabled(True)
        self.interrupt_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.exit_button.setEnabled(False)
        self.append_output("脚本执行已完成。\n")

    def on_script_paused(self):
        self.status_label.setText('脚本状态: 已暂停')
        self.status_label.setStyleSheet("background-color: orange;")
        self.interrupt_button.setEnabled(False)
        self.resume_button.setEnabled(True)
        self.append_output("脚本执行已暂停\n")

    def on_script_resumed(self):
        self.status_label.setText('脚本状态: 运行中')
        self.status_label.setStyleSheet("background-color: green;")
        self.interrupt_button.setEnabled(True)
        self.resume_button.setEnabled(False)
        self.append_output("脚本执行已恢复\n")

    def on_interrupt_occurred(self):
        self.interrupt_button.setEnabled(False)
        self.resume_button.setEnabled(True)
        self.exit_button.setEnabled(True)

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