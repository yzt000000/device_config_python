# utils.py

import os
import glob
import tempfile
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QProcess

def find_gvim():
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
    gvim_location = find_gvim()

    try:
        with open(temp_file_name, 'w') as file:
            file.write(self.script_input.toPlainText())
    except Exception as e:
        QMessageBox.critical(self, '错误', f'无法写入临时文件: {str(e)}')
        return

    process = QProcess(self)
    process.finished.connect(lambda exit_code, exit_status: on_vi_finished(self, temp_file_name, exit_code, exit_status))
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
        set_progress_bar_style(self, temperature)
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