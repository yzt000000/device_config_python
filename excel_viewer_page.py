import sys
import pandas as pd
import math
import re
import pickle
from usb_i2c import USBI2C
from MiniMap import MiniMap

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QSizePolicy,
                             QPushButton, QLabel, QTreeWidget, QTreeWidgetItem, QScrollArea, QFormLayout,
                             QInputDialog, QMessageBox, QLineEdit, QDialog, QComboBox)
from PyQt5.QtGui import QPainter, QColor, QFont , QCursor
from PyQt5.QtCore import Qt, QTimer, QPoint, QRectF


class ExcelViewerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.usb_i2c = USBI2C()
        self.current_page = 0
        self.current_lob = 0
        self.total_pages = 10
        self.setup_gui()
        self.desc_windows = []


    def setup_gui(self):
        self.setWindowTitle("Register Map")
        self.resize(1200, 800)  # 设置窗口的初始大小
        main_layout = QVBoxLayout(self)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        form_layout = QFormLayout()

        # Device address input and update button
        self.device_address_input = QLineEdit(self)
        self.device_address_input.setText("0x6c")
        
        update_address_button = QPushButton('更新设备地址', self)
        update_address_button.clicked.connect(self.update_device_address)

        device_address_layout = QHBoxLayout()
        device_address_layout.addWidget(self.device_address_input)
        device_address_layout.addWidget(update_address_button)
        
        # Add the device address row to the form layout
        form_layout.addRow(QLabel('设备地址:'), device_address_layout)

        # Navigation Frame
        nav_frame = QWidget()
        nav_layout = QHBoxLayout(nav_frame)
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        self.lob_label = QLabel(f"Current LOB: {self.current_lob}")
        self.page_label = QLabel("")
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        nav_layout.addWidget(self.lob_label)
        nav_layout.addWidget(self.page_label)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(nav_frame)

        # Button Frame
        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)
        self.read_button = QPushButton("Read")
        self.read_button.clicked.connect(self.on_read)
        self.write_button = QPushButton("Write")
        self.write_button.clicked.connect(self.on_write)
        self.LOB_L = QLabel(f"Select LOB:")
        
        # LOB ComboBox
        self.lob_combo = QComboBox()
        self.lob_combo.currentIndexChanged.connect(self.on_lob_change)
        button_layout.addWidget(self.LOB_L)
        button_layout.addWidget(self.lob_combo)
        
        self.page_num_button = QPushButton("Set Page Num")
        self.page_num_button.clicked.connect(self.prompt_for_page_num_change)
        self.page_num_label = QLabel(f"Page Num: {self.read_page_num()}")
        button_layout.addWidget(self.read_button)
        button_layout.addWidget(self.write_button)
        button_layout.addWidget(self.page_num_button)
        button_layout.addWidget(self.page_num_label)
        main_layout.addWidget(button_frame)

        # Tree Widget and MiniMap Layout
        tree_mini_map_layout = QHBoxLayout()

        # Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "ADDR", "Default Value", "Access", "Description", "LOB", "Level"])
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 50)
        self.tree.setColumnWidth(2, 50)
        self.tree.setColumnWidth(3, 20)
        self.tree.setColumnWidth(4, 400)
        self.tree.setColumnWidth(5, 20)
        self.tree.setColumnWidth(6, 100)
        self.tree.itemDoubleClicked.connect(self.on_tree_double_click)
        self.tree.setStyleSheet("QTreeWidget::item { height: 30px; }")  # 设置固定行高
        tree_mini_map_layout.addWidget(self.tree)

        # Mini Map
        self.mini_map = MiniMap(self.tree)
        self.mini_map.setFixedSize(200, 600)  # Set a fixed size
        self.mini_map.setVisible(True)  # Ensure it's visible
        tree_mini_map_layout.addWidget(self.mini_map)

        main_layout.addLayout(tree_mini_map_layout)

        self.load_excel_data()
        self.display_current_page()

        # Set up periodic update
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.periodic_update)
        self.timer.start(100)

    def periodic_update(self):
        self.mini_map.update()

    def load_dataframe(self, file_path):
        with open(file_path, 'rb') as f:
            self.excel_data = pickle.load(f)

    def load_excel_data(self):
        self.load_dataframe('register_map_data.pkl')
        #file_path = './xl008_2p0_regmap.xlsx'
        #self.excel_data = pd.read_excel(file_path)

        self.registers_by_lob = {}
        
        for idx, row in self.excel_data.iterrows():
            lob_value = int(row["LOB"]) if pd.notna(row["LOB"]) and row["LOB"] != "default" else "default"
            if lob_value not in self.registers_by_lob:
                self.registers_by_lob[lob_value] = []
                
            if row["TYPE"] == "register":
                self.registers_by_lob[lob_value].append({
                    "NAME": row["NAME"],
                    "ADDR": row["ADDR"],
                    "Default_v_c": row["Default_v_c"],
                    "access": row["access"],
                    "description": row["description"] if pd.notna(row["description"]) else "No description available",
                    "LOB": lob_value,
                    "Level": row["Level"],
                    "fields": []
                })
            elif row["TYPE"] == "field":
                if self.registers_by_lob[lob_value]:
                    self.registers_by_lob[lob_value][-1]["fields"].append({
                        "NAME": row["NAME"],
                        "ADDR": row["ADDR"],
                        "Default_v_c": row["Default_v_c"],
                        "access": row["access"],
                        "description": row["description"] if pd.notna(row["description"]) else "No description available",
                        "LOB": lob_value,
                        "Level": row["Level"]
                    })
                else:
                    print(f"Warning: Field '{row['NAME']}' encountered without a preceding register in LOB '{lob_value}'")
        
        # Calculate default value for each register
        for lob, registers in self.registers_by_lob.items():
            for reg in registers:
                reg["Default_v_c"] = self.calculate_register_default(reg)

        self.pages_by_lob = {}
        self.REGISTERS_PER_PAGE = 32

        for lob, registers in self.registers_by_lob.items():
            pages = [registers[i:i + self.REGISTERS_PER_PAGE] for i in range(0, len(registers), self.REGISTERS_PER_PAGE)]
            self.pages_by_lob[lob] = pages
        
        self.current_lob = list(filter(lambda x: x != "default", self.pages_by_lob.keys()))[0]
        self.total_pages = len(self.pages_by_lob[self.current_lob])
        self.current_page = 1

        # Populate LOB ComboBox
        self.lob_combo.addItems(map(str, filter(lambda x: x != "default", self.pages_by_lob.keys())))
        self.lob_combo.setCurrentText(str(self.current_lob))

    def display_current_page(self):
        self.tree.clear()

        if self.current_lob not in self.pages_by_lob:
            return

        current_lob_registers = self.pages_by_lob[self.current_lob]
        current_page_registers = current_lob_registers[self.current_page - 1]

        for reg in current_page_registers:
            reg_item = QTreeWidgetItem(self.tree)
            reg_item.setText(0, reg["NAME"])
            reg_item.setText(1, reg["ADDR"])
            reg_item.setText(2, reg["Default_v_c"])
            reg_item.setText(3, reg["access"])
            reg_item.setText(4, reg["description"])
            reg_item.setText(5, str(reg["LOB"]))
            reg_item.setText(6, reg["Level"])

            for field in reg["fields"]:
                field_item = QTreeWidgetItem(reg_item)
                field_item.setText(0, field["NAME"])
                field_item.setText(1, field["ADDR"])
                field_item.setText(2, field["Default_v_c"])
                field_item.setText(3, field["access"])
                field_item.setText(4, field["description"])
                field_item.setText(5, str(field["LOB"]))
                field_item.setText(6, field["Level"])

        self.page_label.setText(f"Page {self.current_page} of {self.total_pages}")
        self.lob_label.setText(f"Current LOB: {self.current_lob}")  # 更新当前LOB的显示
        self.mini_map.update()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_current_page()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_current_page()


    def on_read(self):
        selected_items = self.tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            if item.parent() is not None:  # This is a field
                reg_item = item.parent()
            else:  # This is a register
                reg_item = item
            addr = reg_item.text(1)
            value = self.i2c_read(addr)
            reg_item.setText(2, value)
            self.update_fields_default(reg_item, value)

    def on_write(self):
        selected_items = self.tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            if item.parent() is not None:  # This is a field
                reg_item = item.parent()
            else:  # This is a register
                reg_item = item
            addr = reg_item.text(1)
            value = reg_item.text(2)
            self.i2c_write(addr, value)

    def i2c_read(self, addr):
        addr = self.convert_address(addr)
        value = self.usb_i2c.read(int(addr, 16))
        return f"0x{value:02X}"

    def i2c_write(self, addr, value):
        addr = self.convert_address(addr)
        self.usb_i2c.write(int(addr, 16), int(value, 16))


    def convert_address(self, addr):
        # 检查地址格式是否为 '8'hXX'
        if isinstance(addr, str):
            if addr.startswith("8'h"):
                # 移除 '8'h' 前缀，并添加 '0x' 前缀
                return "0x" + addr[3:]
            # 如果已经是 '0xXX' 格式，直接返回
            elif addr.startswith("8‘h"):
                return "0x" + addr[3:]
            # 如果已经是 '0xXX' 格式，直接返回
            elif addr.startswith("0x"):
                return addr
            # 如果是纯数字，添加 '0x' 前缀
            else:
                return "0x" + addr
        # 如果是整数，转换为十六进制字符串
        elif isinstance(addr, int):
            return f"0x{addr:02X}"
        else:
            raise ValueError("Invalid address format")

    # def show_description(self, item):
    #     description = item.text(4)
    #     if pd.isna(description):
    #         description = "No description available"
    #     desc_window = QDialog(self)
    #     desc_window.setWindowTitle("Description")
    #     layout = QVBoxLayout(desc_window)
    #     text_edit = QLineEdit(description)
    #     text_edit.setReadOnly(True)
    #     layout.addWidget(text_edit)
        
    #     # 获取鼠标当前位置
    #     cursor_pos = self.mapToGlobal(QPoint(0, 0))
    #     desc_window.setGeometry(cursor_pos.x() + 10, cursor_pos.y() + 10, 400, 100)
        
    #     desc_window.show()
    #     self.desc_windows.append(desc_window)
    #     if len(self.desc_windows) > 2:
    #         old_window = self.desc_windows.pop(0)
    #         old_window.close()
    



    def show_description(self, item):
        description = item.text(4)
        if pd.isna(description):
            description = "No description available"
        desc_window = QDialog(self)
        desc_window.setWindowTitle("Description")
        layout = QVBoxLayout(desc_window)
        
        text_edit = QTextEdit()
        text_edit.setPlainText(description)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        # 获取鼠标当前位置
        #cursor_pos = self.mapToGlobal(QPoint(0, 0))
        cursor_pos = QCursor.pos()
        desc_window.setGeometry(cursor_pos.x() + 10, cursor_pos.y() + 10, 400, 300)  # 设置初始大小
        
        desc_window.show()
        self.desc_windows.append(desc_window)
        if len(self.desc_windows) > 2:
            old_window = self.desc_windows.pop(0)
            old_window.close()

    def on_tree_double_click(self, item, column):
        if column == 4:  # Description column
            self.show_description(item)
        elif column == 2:  # Default Value column
            self.on_edit(item)


    

    def on_edit(self, item):
        old_value = item.text(2)
        new_value, ok = QInputDialog.getText(self, "Edit Default Value", "Enter new value:", QLineEdit.Normal, old_value)
        if ok:
            item.setText(2, new_value)
            if item.parent() is None:  # This is a register
                self.update_fields_default(item, new_value)
                addr = item.text(1)
                self.i2c_write(addr, new_value)
            else:  # This is a field
                reg_item = item.parent()
                self.update_register_default(reg_item)
                new_reg_value = reg_item.text(2)
                addr = reg_item.text(1)  # Use the register's address
                self.i2c_write(addr, new_reg_value)

    def update_fields_default(self, reg_item, new_reg_value):
        new_reg_value = int(new_reg_value, 16)
        for i in range(reg_item.childCount()):
            field_item = reg_item.child(i)
            addr = field_item.text(1)
            high, low = self.parse_address(addr)
            if high is None or low is None:
                continue
            mask = ((1 << (high - low + 1)) - 1) << low
            shift = low
            field_value = (new_reg_value & mask) >> shift
            field_item.setText(2, f"0x{field_value:X}")

    def update_register_default(self, reg_item):
        register = {"fields": []}
        for i in range(reg_item.childCount()):
            field_item = reg_item.child(i)
            register["fields"].append({
                "NAME": field_item.text(0),
                "ADDR": field_item.text(1),
                "Default_v_c": field_item.text(2),
                "access": field_item.text(3),
                "description": field_item.text(4),
                "LOB": field_item.text(5),
                "Level": field_item.text(6)
            })
        new_default = self.calculate_register_default(register)
        reg_item.setText(2, new_default)

    def clean_address(self, addr):
        return re.sub(r"8'h", "", addr)

    def parse_address(self, addr_str):
        if isinstance(addr_str, str):
            range_match = re.match(r'\[(\d+):(\d+)\]', addr_str)
            single_bit_match = re.match(r'\[(\d+)\]', addr_str)
            if range_match:
                high, low = map(int, range_match.groups())
                return high, low
            elif single_bit_match:
                bit = int(single_bit_match.group(1))
                return bit, bit
            else:
                try:
                    single_bit = int(addr_str)
                    return single_bit, single_bit
                except ValueError:
                    return None, None
        elif isinstance(addr_str, (int, float)):
            return int(addr_str), int(addr_str)
        return None, None

    def calculate_register_default(self, register):
        default_value = 0
        for field in register["fields"]:
            high, low = self.parse_address(field["ADDR"])
            if high is None or low is None:
                continue

            mask = ((1 << (high - low + 1)) - 1) << low
            shift = low

            if isinstance(field["Default_v_c"], str) and field["Default_v_c"].startswith("0x"):
                field_value = int(field["Default_v_c"], 16)
            elif isinstance(field["Default_v_c"], (int, float)):
                field_value = int(field["Default_v_c"])
            else:
                field_value = 0

            default_value |= (field_value << shift) & mask

        return f"0x{default_value:02X}"

    def on_lob_change(self, index):
        new_lob = int(self.lob_combo.currentText())
        self.change_lob(new_lob)

    def change_lob(self, new_lob):
        if new_lob in self.pages_by_lob:
            self.current_lob = new_lob
            self.total_pages = len(self.pages_by_lob[self.current_lob])
            self.current_page = 1
            self.display_current_page()
        else:
            QMessageBox.warning(self, "LOB Not Found", f"LOB {new_lob} does not exist in the data.")

    def prompt_for_page_num_change(self):
        new_page_num, ok = QInputDialog.getInt(self, "Set Page Num", "Enter new page number:", self.current_page, 0, self.total_pages)
        if ok:
            if 0 <= new_page_num <= self.total_pages:
                self.current_page = new_page_num
                self.write_page_num(new_page_num)
                self.display_current_page()
                self.page_num_label.setText(f"Page Num: {new_page_num}")
            else:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid page number.")

    def read_page_num(self):
        value = self.i2c_read("0xF0")
        return int(value, 16)

    def write_page_num(self, page_num):
        self.i2c_write("0xF0", f"0x{page_num:02X}")

    def periodic_update(self):
        self.mini_map.update()


    def update_device_address(self):
        try:
            self.device_address = int(self.device_address_input.text(), 16)
            #self.append_output(f'设备地址更新为: 0x{self.device_address:02X}\n')
            self.usb_i2c.update_device_address(self.device_address)  # 调用usb_i2c的更新方法
        except ValueError:
            QMessageBox.critical(self, '错误', '无效的设备地址')
