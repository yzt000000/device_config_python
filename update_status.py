# import json
# import random
# from PyQt5.QtWidgets import (
# QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpacerItem, QSizePolicy,
# QPushButton, QPlainTextEdit, QTextEdit, QMessageBox, QFileDialog, QTabWidget, QProgressBar,
# QGridLayout, QFormLayout, QTreeWidget, QTreeWidgetItem, QDialog, QComboBox
# )
# from PyQt5.QtCore import Qt
# from usb_i2c import USBI2C
# class UpdateStatus(QWidget):
#     def __init__(self,global_usb_i2c,global_device_address):
#         super().__init__()
#         self.init_ui()
#         self.usb_i2c = global_usb_i2c
#         self.device_address = global_device_address  # Initialize with None
#         self.load_config('config.json')

#     def init_ui(self):
#         layout = QVBoxLayout()
#         form_layout = QFormLayout()

#         # Register address selection
#         self.register_address_combo = QComboBox(self)
#         self.register_address_combo.currentIndexChanged.connect(self.update_status)

#         self.update_button = QPushButton('更新状态', self)
#         self.update_button.clicked.connect(self.update_status)

#         self.update_all_button = QPushButton('更新所有状态', self)
#         self.update_all_button.clicked.connect(self.update_all_statuses)
#         form_layout.addRow(self.update_all_button)
        

#         form_layout.addRow(QLabel('寄存器地址:'), self.register_address_combo)
#         form_layout.addRow(self.update_button)

#         self.status_output = QTextEdit(self)
#         self.status_output.setReadOnly(True)
#         self.status_output.setAcceptRichText(True)  # 允许富文本

#         layout.addLayout(form_layout)
#         layout.addWidget(QLabel('状态输出:'))
#         layout.addWidget(self.status_output)

#         self.setLayout(layout) 



#     def load_config(self, config_file):
#         try:
#             with open(config_file, 'r', encoding='utf-8') as file:
#                 self.config = json.load(file)
#             self.register_address_combo.clear()
#             self.register_address_combo.addItems(self.config.keys())
#         except json.JSONDecodeError as e:
#             QMessageBox.critical(self, '错误', f'JSON 解析错误: {str(e)}')
#             self.config = {}
#         except FileNotFoundError:
#             QMessageBox.critical(self, '错误', f'找不到配置文件: {config_file}')
#             self.config = {}
#         except Exception as e:
#             QMessageBox.critical(self, '错误', f'加载配置文件时出错: {str(e)}')
#             self.config = {}


#     def update_device_address(self):
#         new_address = self.device_address_input.text()
#         try:
#             self.usb_i2c.set_address(int(new_address, 16))
#             QMessageBox.information(self, '成功', '设备地址更新成功')
#         except Exception as e:
#             QMessageBox.critical(self, '错误', f'更新设备地址失败: {str(e)}')

    
    
#     def update_all_statuses(self):
#         self.status_output.clear()
#         for register_address in self.config:
#             register_config = self.config[register_address]
#             try:
#                 data = self.read_i2c(int(register_address, 16))
#                 status_text = self.parse_status(data, register_config, register_address)
#                 self.status_output.append(status_text)
#                 self.status_output.append('<br/>')  # 在每个寄存器的输出之间添加空行
#             except Exception as e:
#                 error_message = f'<span style="color: red;">读取寄存器 {register_address} 时出错: {str(e)}</span><br/>'
#                 self.status_output.append(error_message)

#     def update_status(self):
#         register_address = self.register_address_combo.currentText()
#         if register_address not in self.config:
#             QMessageBox.critical(self, '错误', '未知的寄存器地址')
#             return

#         register_config = self.config[register_address]
#         try:
#             data = self.read_i2c(int(register_address, 16))
#             status_text = self.parse_status(data, register_config, register_address)
#             self.status_output.setHtml(status_text)  # 使用 setHtml 而不是 setPlainText
#         except Exception as e:
#             error_message = f'<span style="color: red;">更新状态失败: {str(e)}</span>'
#             self.status_output.setHtml(error_message)

#     def parse_status(self, data, register_config, register_address):
#         status_text = f'<b>寄存器地址:</b> {register_address}: <b>寄存器值:</b> 0x{data:02X}<br/>'

#         # 处理 bits
#         if 'bits' in register_config:
#             #status_text += '<b>Bits:</b><br/>'
#             for bit_info in register_config['bits']:
#                 bit_value = (data >> bit_info['bit']) & 1
#                 #status_text += f"&nbsp;&nbsp;{bit_info['name']}: {bit_value}:     "
#                 if 'messages' in bit_info:
#                     message_info = bit_info['messages'].get(str(bit_value), {'text': '未知状态', 'color': 'black', 'size': '12px'})
#                     status_text += f"<span style='color: {message_info['color']}; font-size: {message_info['size']};'>{message_info['text']}</span><br/>"

#         # 处理 values
#         if 'values' in register_config:
#             value_matched = False
#             for value_info in register_config['values']:
#                 if data == int(value_info['value'], 16):
#                     #status_text += f"<b>匹配的值:</b> {value_info['name']}  "
#                     if 'messages' in value_info:
#                         status_text += f"<span style='color: {value_info.get('color', 'black')}; font-size: {value_info.get('size', '12px')};'>详细信息: {value_info['messages']}</span><br/>"
#                     value_matched = True
#                     break
#             if not value_matched:
#                 status_text += "<span style='color: red;'>未匹配到特定值</span><br/>"

#         # 处理 calculation
#         if 'calculation' in register_config:
#             try:
#                 calc_config = register_config['calculation']
#                 calculated_value = eval(calc_config['formula'].replace('data', str(data)))
#                 formatted_result = calc_config['print_format'].format(result=calculated_value)
#                 status_text += f"<span style='color: {calc_config.get('color', 'black')}; font-size: {calc_config.get('size', '12px')};'><b>计算结果:</b> {formatted_result}</span><br/>"
#             except Exception as e:
#                 status_text += f"<span style='color: red;'>计算错误:</span> {str(e)}<br/>"

#         # 处理 bit_fields
#         if 'bit_fields' in register_config:
#             #status_text += '<b>Bit Fields:</b><br/>'
#             for bit_field in register_config['bit_fields']:
#                 field_value = (data >> bit_field['start_bit']) & ((1 << bit_field['length']) - 1)
                
#                 matched_value = next((item for item in bit_field['values'] if int(item['value'], 16) == field_value), None)
                
#                 if matched_value:
#                     field_name = matched_value['name']
#                     #status_text += f"&nbsp;&nbsp;{bit_field['start_bit'] + bit_field['length'] - 1}:{bit_field['start_bit']} 位域: {field_name}:    "
#                     if 'messages' in matched_value:
#                         color = matched_value.get('color', 'black')
#                         size = matched_value.get('size', '12px')
#                         status_text += f"<span style='color: {color}; font-size: {size};'>{matched_value['messages']}</span><br/>"
#                 else:
#                     status_text += f"&nbsp;&nbsp;{bit_field['start_bit'] + bit_field['length'] - 1}:{bit_field['start_bit']} 位域: <span style='color: red;'>未知值 (0x{field_value:02X})</span><br/>"

#         return status_text


#     def read_i2c(self, register_address):
#         # 模拟读取I2C寄存器值
#         #return 0x55  # 替换为实际的I2C读取逻辑
#         return random.randint(0, 0xFF)
#     # def read_i2c(self, register_address):
#     #     if self.device_address is None:
#     #         raise ValueError('设备地址未设置')
#     #     #return self.usb_i2c.read_register(self.device_address, register_address)
#     #     return self.usb_i2c.read(register_address)

# if __name__ == '__main__':
#     import sys
#     app = QApplication(sys.argv)
#     window = UpdateStatus()
#     window.show()
#     sys.exit(app.exec_())


################################################################


import json
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpacerItem, QSizePolicy,
    QPushButton, QPlainTextEdit, QTextEdit, QMessageBox, QFileDialog, QTabWidget, QProgressBar,
    QGridLayout, QFormLayout, QTreeWidget, QTreeWidgetItem, QDialog, QComboBox
)
from PyQt5.QtCore import Qt
from usb_i2c import USBI2C

class UpdateStatus(QWidget):
    def __init__(self, global_usb_i2c, global_device_address):
        super().__init__()
        self.init_ui()
        self.usb_i2c = global_usb_i2c
        self.device_address = global_device_address  # Initialize with None
        self.load_config('config.json')

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Register address selection
        self.register_address_combo = QComboBox(self)
        self.register_address_combo.currentIndexChanged.connect(self.update_status)

        self.load_config_button = QPushButton('加载配置文件', self)
        self.load_config_button.clicked.connect(self.load_config_dialog)
        form_layout.addRow(self.load_config_button)

        self.update_button = QPushButton('更新状态', self)
        self.update_button.clicked.connect(self.update_status)

        self.update_all_button = QPushButton('更新所有状态', self)
        self.update_all_button.clicked.connect(self.update_all_statuses)
        form_layout.addRow(self.update_all_button)


        form_layout.addRow(QLabel('寄存器地址:'), self.register_address_combo)
        form_layout.addRow(self.update_button)

        self.status_output = QTextEdit(self)
        self.status_output.setReadOnly(True)
        self.status_output.setAcceptRichText(True)  # 允许富文本

        layout.addLayout(form_layout)
        layout.addWidget(QLabel('状态输出:'))
        layout.addWidget(self.status_output)

        self.setLayout(layout)

    def load_config_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "加载配置文件", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_path:
            self.load_config(file_path)

    def load_config(self, config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
            self.register_address_combo.clear()
            self.register_address_combo.addItems(self.config.keys())
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, '错误', f'JSON 解析错误: {str(e)}')
            self.config = {}
        except FileNotFoundError:
            QMessageBox.critical(self, '错误', f'找不到配置文件: {config_file}')
            self.config = {}
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载配置文件时出错: {str(e)}')
            self.config = {}

    def update_device_address(self):
        new_address = self.device_address_input.text()
        try:
            self.usb_i2c.set_address(int(new_address, 16))
            QMessageBox.information(self, '成功', '设备地址更新成功')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'更新设备地址失败: {str(e)}')

    def update_all_statuses(self):
        self.status_output.clear()
        for register_address in self.config:
            register_config = self.config[register_address]
            try:
                data = self.read_i2c(int(register_address, 16))
                status_text = self.parse_status(data, register_config, register_address)
                self.status_output.append(status_text)
                self.status_output.append('<br/>')  # 在每个寄存器的输出之间添加空行
            except Exception as e:
                error_message = f'<span style="color: red;">读取寄存器 {register_address} 时出错: {str(e)}</span><br/>'
                self.status_output.append(error_message)

    def update_status(self):
        register_address = self.register_address_combo.currentText()
        if register_address not in self.config:
            QMessageBox.critical(self, '错误', '未知的寄存器地址')
            return

        register_config = self.config[register_address]
        try:
            data = self.read_i2c(int(register_address, 16))
            status_text = self.parse_status(data, register_config, register_address)
            self.status_output.setHtml(status_text)  # 使用 setHtml 而不是 setPlainText
        except Exception as e:
            error_message = f'<span style="color: red;">更新状态失败: {str(e)}</span>'
            self.status_output.setHtml(error_message)

    def parse_status(self, data, register_config, register_address):
        status_text = f'<b>寄存器地址:</b> {register_address}: <b>寄存器值:</b> 0x{data:02X}<br/>'

        # 处理 bits
        if 'bits' in register_config:
            for bit_info in register_config['bits']:
                bit_value = (data >> bit_info['bit']) & 1
                if 'messages' in bit_info:
                    message_info = bit_info['messages'].get(str(bit_value), {'text': '未知状态', 'color': 'black', 'size': '12px'})
                    status_text += f"<span style='color: {message_info['color']}; font-size: {message_info['size']};'>{message_info['text']}</span><br/>"

        # 处理 values
        if 'values' in register_config:
            value_matched = False
            for value_info in register_config['values']:
                if data == int(value_info['value'], 16):
                    if 'messages' in value_info:
                        status_text += f"<span style='color: {value_info.get('color', 'black')}; font-size: {value_info.get('size', '12px')};'>详细信息: {value_info['messages']}</span><br/>"
                    value_matched = True
                    break
            if not value_matched:
                status_text += "<span style='color: red;'>未匹配到特定值</span><br/>"

        # 处理 calculation
        if 'calculation' in register_config:
            try:
                calc_config = register_config['calculation']
                calculated_value = eval(calc_config['formula'].replace('data', str(data)))
                formatted_result = calc_config['print_format'].format(result=calculated_value)
                status_text += f"<span style='color: {calc_config.get('color', 'black')}; font-size: {calc_config.get('size', '12px')};'><b>计算结果:</b> {formatted_result}</span><br/>"
            except Exception as e:
                status_text += f"<span style='color: red;'>计算错误:</span> {str(e)}<br/>"

        # 处理 bit_fields
        if 'bit_fields' in register_config:
            for bit_field in register_config['bit_fields']:
                field_value = (data >> bit_field['start_bit']) & ((1 << bit_field['length']) - 1)
                matched_value = next((item for item in bit_field['values'] if int(item['value'], 16) == field_value), None)
                if matched_value:
                    if 'messages' in matched_value:
                        color = matched_value.get('color', 'black')
                        size = matched_value.get('size', '12px')
                        status_text += f"<span style='color: {color}; font-size: {size};'>{matched_value['messages']}</span><br/>"
                else:
                    status_text += f"&nbsp;&nbsp;{bit_field['start_bit'] + bit_field['length'] - 1}:{bit_field['start_bit']} 位域: <span style='color: red;'>未知值 (0x{field_value:02X})</span><br/>"

        return status_text

    def read_i2c(self, register_address):
        return random.randint(0, 0xFF)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = UpdateStatus(None, None)
    window.show()
    sys.exit(app.exec_())
