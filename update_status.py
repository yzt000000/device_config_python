#############################################################################################################
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
        self.load_sequence_config('sequence_config.json')  # 初始化时加载 sequence_config.json

    def init_ui(self):
        layout = QVBoxLayout()

        # 第一行：加载配置文件和加载序列操作
        top_row_layout = QHBoxLayout()
        self.load_config_button = QPushButton('加载配置文件: config.json', self)
        self.load_config_button.clicked.connect(self.load_config_dialog)
        top_row_layout.addWidget(self.load_config_button)

        self.load_sequence_config_button = QPushButton('加载序列配置文件: sequence_config.json', self)
        self.load_sequence_config_button.clicked.connect(self.load_sequence_config_dialog)
        top_row_layout.addWidget(self.load_sequence_config_button)

        layout.addLayout(top_row_layout)

        # 第二行：寄存器地址，更新状态，更新所有状态，执行序列操作
        bottom_row_layout = QHBoxLayout()

        self.register_address_combo = QComboBox(self)
        self.register_address_combo.currentIndexChanged.connect(self.update_status)
        bottom_row_layout.addWidget(QLabel('寄存器地址:'))
        bottom_row_layout.addWidget(self.register_address_combo)

        self.update_button = QPushButton('更新状态', self)
        self.update_button.clicked.connect(self.update_status)
        bottom_row_layout.addWidget(self.update_button)

        self.update_all_button = QPushButton('更新所有状态', self)
        self.update_all_button.clicked.connect(self.update_all_statuses)
        bottom_row_layout.addWidget(self.update_all_button)

        self.execute_sequence_button = QPushButton('执行序列操作', self)
        self.execute_sequence_button.clicked.connect(self.execute_sequence)
        bottom_row_layout.addWidget(self.execute_sequence_button)

        layout.addLayout(bottom_row_layout)

        self.status_output = QTextEdit(self)
        self.status_output.setReadOnly(True)
        self.status_output.setAcceptRichText(True)  # 允许富文本

        layout.addWidget(QLabel('状态输出:'))
        layout.addWidget(self.status_output)

        self.setLayout(layout)

    def load_config_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "加载配置文件", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_path:
            self.load_config(file_path)
            self.load_config_button.setText(f'加载配置文件: {file_path}')

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

    def load_sequence_config_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "加载序列配置文件", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_path:
            self.load_sequence_config(file_path)
            self.load_sequence_config_button.setText(f'加载序列配置文件: {file_path}')

    def load_sequence_config(self, config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                self.sequence_config = json.load(file)
            #QMessageBox.information(self, '成功', '序列配置文件加载成功')
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, '错误', f'JSON 解析错误: {str(e)}')
            self.sequence_config = {}
        except FileNotFoundError:
            QMessageBox.critical(self, '错误', f'找不到配置文件: {config_file}')
            self.sequence_config = {}
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载序列配置文件时出错: {str(e)}')
            self.sequence_config = {}

    def execute_sequence(self):
        if not self.sequence_config:
            QMessageBox.critical(self, '错误', '请先加载配置文件')
            return

        self.status_output.clear()
        for register_address in self.sequence_config:
            register_config = self.sequence_config[register_address]
            try:
                if 'read' in register_config:
                    data = self.read_i2c(int(register_address, 16))
                    status_text = self.parse_status(data, register_config['read'], register_address)
                    self.status_output.append(status_text)
                if 'write' in register_config:
                    self.write_status(int(register_address, 16), register_config['write'])
                    self.status_output.append(f'<b>写入寄存器 {register_address}:</b> 完成<br/>')
                self.status_output.append('<br/>')  # 在每个操作的输出之间添加空行
            except Exception as e:
                error_message = f'<span style="color: red;">执行操作 {register_address} 时出错: {str(e)}</span><br/>'
                self.status_output.append(error_message)

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
            register_config = self.config[register_address].get('read', {})
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
        
        # 检查 register_address 是否为空
        if not register_address:
            error_message = '<span style="color: red;">寄存器地址不能为空</span>'
            self.status_output.setHtml(error_message)
            return

        if register_address not in self.config:
            error_message = '<span style="color: red;">未知的寄存器地址</span>'
            self.status_output.setHtml(error_message)
            return

        register_config = self.config[register_address].get('read', {})
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
                    if(message_info['size'] == '1px'):
                        pass
                    else:
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
                #status_text += "<span style='color: red;'>未匹配到特定值</span><br/>"
                status_text += "<span style='color: red;'>0x{data:02x}</span><br/>"

        # 处理 calculation
        if 'calculation' in register_config:
            try:
                calc_config = register_config['calculation']
                calculated_value = eval(calc_config['formula'].replace('data', str(data)))
                formatted_result = calc_config['print_format'].format(result=calculated_value)
                status_text += f"<span style='color: {calc_config.get('color', 'black')}; font-size: {calc_config.get('size', '12px')};'><b>Cal:</b> {formatted_result}</span><br/>"
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

    # def read_i2c(self, register_address):
    #     #return random.randint(0, 0xFF)
    #     #return 0x00
    #     value = 0
    #     return f"0x{value:02X}"
        

    # def write_i2c(self, register_address, data):
    #     # 这里添加实际的 I2C 写操作逻辑
    #     pass
    def convert_address(self, addr):
        if isinstance(addr, str):
            if addr.startswith("8'h"):
                return "0x" + addr[3:]
            elif addr.startswith("8‘h"):
                return "0x" + addr[3:]
            elif addr.startswith("0x"):
                return addr
            else:
                return "0x" + addr
        elif isinstance(addr, int):
            return f"0x{addr:02X}"
        else:
            raise ValueError("Invalid address format")

    def read_i2c(self, addr):
        addr = self.convert_address(addr)
        value = self.usb_i2c.read(int(addr, 16))
        #return f"0x{value:02X}"
        return value

    def write_i2c(self, addr, value):
        addr = self.convert_address(addr)
        #self.usb_i2c.write(int(addr, 16), int(value, 16))
        self.usb_i2c.write(int(addr, 16), value)

    def write_status(self, register_address, write_config):
        try:
            current_data = self.read_i2c(register_address)
            new_data = current_data
            modified_messages = []

            if 'bits' in write_config:
                for bit_info in write_config['bits']:
                    bit_value = int(bit_info['value'], 16)
                    current_bit_value = (current_data >> bit_info['bit']) & 1
                    if current_bit_value != bit_value:
                        modified_messages.append((bit_info['messages'], bit_info['color'], bit_info['size']))
                    if bit_value == 1:
                        new_data |= (1 << bit_info['bit'])
                    else:
                        new_data &= ~(1 << bit_info['bit'])

            if 'values' in write_config:
                for value_info in write_config['values']:
                    new_data = int(value_info['value'], 16)
                    modified_messages.append((value_info['messages'], value_info['color'], value_info['size']))

            if 'bit_fields' in write_config:
                for bit_field in write_config['bit_fields']:
                    field_value = int(bit_field['values'][0]['value'], 16)
                    mask = ((1 << bit_field['length']) - 1) << bit_field['start_bit']
                    current_field_value = (current_data >> bit_field['start_bit']) & ((1 << bit_field['length']) - 1)
                    if current_field_value != field_value:
                        modified_messages.append((bit_field['values'][0]['messages'], bit_field['values'][0]['color'], bit_field['values'][0]['size']))
                    new_data = (new_data & ~mask) | ((field_value << bit_field['start_bit']) & mask)

            self.write_i2c(register_address, new_data)
            self.status_output.append(f'<b>写入寄存器 {register_address}:</b> 0x{new_data:02X}<br/>')

            for message, color, size in modified_messages:
                self.status_output.append(f"<span style='color: {color}; font-size: {size};'>{message}</span><br/>")

        except Exception as e:
            error_message = f'<span style="color: red;">写入寄存器 {register_address} 时出错: {str(e)}</span><br/>'
            self.status_output.append(error_message)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = UpdateStatus(None, None)
    window.show()
    sys.exit(app.exec_())