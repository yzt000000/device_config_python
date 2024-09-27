import sys
import math
import re
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, 
                             QComboBox, QPushButton, QFileDialog, QHBoxLayout, QHeaderView, QLabel, QMessageBox, 
                             QDialog, QTextEdit, QScrollBar, QSplitter)
from PyQt5.QtCore import Qt, QEvent, QTimer, QRectF
from PyQt5.QtGui import QCursor, QPainter, QColor, QPen

class MiniMapWidget(QWidget):
    def __init__(self, tree_widget, parent=None):
        super().__init__(parent)
        self.tree_widget = tree_widget
        self.setFixedWidth(100)  # 设置minimap的宽度
        self.tree_widget.verticalScrollBar().valueChanged.connect(self.update)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制背景
        painter.fillRect(self.rect(), QColor(240, 240, 240))

        if self.tree_widget.topLevelItemCount() == 0:
            return

        # 计算比例
        visible_height = self.tree_widget.viewport().height()
        total_height = self.tree_widget.verticalScrollBar().maximum() + visible_height
        scale = self.height() / total_height if total_height > 0 else 1

        # 绘制所有项目
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            item_rect = self.tree_widget.visualItemRect(item)
            minimap_rect = QRectF(0, item_rect.top() * scale, self.width(), max(1, item_rect.height() * scale))
            painter.fillRect(minimap_rect, QColor(200, 200, 200))

        # 绘制当前可见区域
        scroll_value = self.tree_widget.verticalScrollBar().value()
        visible_rect = QRectF(0, scroll_value * scale, self.width(), visible_height * scale)
        painter.setPen(QPen(QColor(0, 0, 255), 2))
        painter.drawRect(visible_rect)


def hex_format(x):
    if pd.isna(x) or x == '':
        return ''
    if isinstance(x, str) and x.startswith('0x'):
        return x.upper()
    try:
        return f"0x{int(x):X}"
    except ValueError:
        return str(x)



class DescriptionPopup(QDialog):
    def __init__(self, parent=None, description=""):
        super().__init__(parent)
        self.setWindowTitle("Description")
        self.setGeometry(100, 100, 300, 200)
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(description)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

class EditableTreeWidget(QTreeWidget):
    def __init__(self, register_viewer):
        super().__init__()
        self.register_viewer = register_viewer
        self.setEditTriggers(QTreeWidget.DoubleClicked)
        self.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.viewport():
            if event.type() == QEvent.MouseButtonDblClick:
                item = self.itemAt(event.pos())
                if item:
                    column = self.columnAt(event.pos().x())
                    if column == 4:  # Description column
                        self.register_viewer.show_description_popup(item, event.globalPos())
                        return True
        return super().eventFilter(obj, event)

class RegisterViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_user_edit = False
        self.setWindowTitle("Register Viewer")
        self.setGeometry(100, 100, 1300, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 创建一个新的布局来容纳左侧的按钮和选择器
        self.left_layout = QHBoxLayout()
        
        # 添加寄存器读写按钮
        self.read_button = QPushButton("Read Register")
        self.write_button = QPushButton("Write Register")
        self.read_button.clicked.connect(self.read_register)
        self.write_button.clicked.connect(self.write_register)
        self.left_layout.addWidget(self.read_button)
        self.left_layout.addWidget(self.write_button)

        # 创建水平布局，用于放置 book_label 和 book_selector
        book_layout = QHBoxLayout()
        book_layout.setSpacing(0)  # 设置布局的间距为0

        self.book_label = QLabel("BOOK:")
        self.book_selector = QComboBox()

        book_layout.addWidget(self.book_label)
        book_layout.addWidget(self.book_selector)

        # 创建水平布局，用于放置 page_label 和 page_selector
        page_layout = QHBoxLayout()
        page_layout.setSpacing(0)  # 设置布局的间距为0

        self.page_label = QLabel("PAGE:")
        self.page_selector = QComboBox()

        page_layout.addWidget(self.page_label)
        page_layout.addWidget(self.page_selector)

        # 将 book_layout 和 page_layout 添加到左侧布局中
        self.left_layout.addLayout(book_layout)
        self.left_layout.addLayout(page_layout)



        # 添加 Load Excel File 按钮
        self.load_button = QPushButton("Load Excel File")
        self.load_button.clicked.connect(self.load_excel)
        self.left_layout.addWidget(self.load_button)

        # 创建另一个布局来容纳右侧的按钮
        self.right_layout = QHBoxLayout()
        
        # 添加 Previous 和 Next 按钮
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)
        self.right_layout.addWidget(self.prev_button)
        self.right_layout.addWidget(self.next_button)

        # 添加 Expand All 按钮
        self.expand_button = QPushButton("Expand All")
        self.expand_button.clicked.connect(self.expand_all)
        self.right_layout.addWidget(self.expand_button)

        # 添加 Collapse All 按钮
        self.collapse_button = QPushButton("Collapse All")
        self.collapse_button.clicked.connect(self.collapse_all)
        self.right_layout.addWidget(self.collapse_button)

        # 添加 Page Label
        self.page_label = QLabel()
        self.right_layout.addWidget(self.page_label)

        # 将这两个布局添加到一个水平布局中
        self.top_layout = QHBoxLayout()
        self.top_layout.addLayout(self.left_layout)
        self.top_layout.addLayout(self.right_layout)

        # 将顶部的水平布局添加到主布局中
        self.layout.addLayout(self.top_layout)

        # 创建水平布局来容纳树形控件和minimap
        splitter = QSplitter(Qt.Horizontal)
        # 添加树形控件
        self.tree = EditableTreeWidget(self)
        #self.tree.setHeaderLabels(["NAME", "ADDR", "Default_v_c", "access", "Description", "Level", "shadow", "Bit"])
        self.tree.setHeaderLabels(["NAME", "ADDR", "Default_v_c", "access", "Description", "Level"])
        self.tree.itemChanged.connect(self.on_item_changed)
        self.layout.addWidget(self.tree)

        # 创建并添加minimap
        self.minimap = MiniMapWidget(self.tree)
        splitter.addWidget(self.minimap)
        # 设置splitter的初始大小
        splitter.setSizes([1000, 100])  # 树形控件占大部分宽度，minimap占较小部分

        # 将布局添加到主布局
        self.layout.addLayout(self.top_layout)
        self.layout.addWidget(splitter)


        # 初始化弹出窗口列表
        self.popup_windows = []

        # 连接选择器和按钮的信号
        self.book_selector.currentIndexChanged.connect(self.update_page_selector)
        self.page_selector.currentIndexChanged.connect(self.display_registers)
        self.tree.itemSelectionChanged.connect(self.update_rw_buttons)
        self.tree.itemChanged.connect(self.on_item_changed)
        self.tree.itemDoubleClicked.connect(self.on_item_edit_started)

        self.df = None
        self.current_page = 1
        self.registers_per_page = 64

    def load_excel(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx *.xls)")
        if file_name:
            self.df = pd.read_excel(file_name, sheet_name='regmap')
            self.df = self.df.fillna('')
            self.df['Book'] = self.df['Book'].apply(hex_format)
            self.df['PAGE'] = self.df['PAGE'].apply(hex_format)
            self.update_book_selector()

    def update_book_selector(self):
        if self.df is not None:
            books = self.df['Book'].unique()
            self.book_selector.clear()
            self.book_selector.addItems([str(book) for book in books])

    def update_page_selector(self):
        if self.df is not None:
            current_book = self.book_selector.currentText()
            pages = self.df[self.df['Book'] == current_book]['PAGE'].unique()
            self.page_selector.clear()
            self.page_selector.addItems([str(page) for page in pages])



    def show_description_popup(self, item, global_pos):
            description = item.text(4)  # Get the description from the 5th column
            if description:
                popup = DescriptionPopup(self, description)
                popup.move(global_pos)
                popup.show()

                # 添加新的弹出窗口到列表
                self.popup_windows.append(popup)

                # 如果弹出窗口数量超过3个，关闭最早的窗口
                if len(self.popup_windows) > 3:
                    oldest_popup = self.popup_windows.pop(0)
                    oldest_popup.close()

                # 设置定时器在30秒后自动关闭窗口
                QTimer.singleShot(30000, popup.close)

    def display_registers(self):
        if self.df is not None:
            self.is_user_edit = False  # Set flag to False before updating tree
            current_book = self.book_selector.currentText()
            current_page = self.page_selector.currentText()

            filtered_df = self.df[(self.df['Book'] == current_book) & (self.df['PAGE'] == current_page)]
            self.tree.clear()

            registers = filtered_df[filtered_df['Registers'] == 'register']

            total_registers = len(registers)
            total_pages = math.ceil(total_registers / self.registers_per_page)

            start_index = (self.current_page - 1) * self.registers_per_page
            end_index = start_index + self.registers_per_page

            for register_idx in range(start_index, min(end_index, total_registers)):
                register_row = registers.iloc[register_idx]
                register_item = QTreeWidgetItem(self.tree)
                self.set_item_values(register_item, register_row)
                register_item.setFlags(register_item.flags() | Qt.ItemIsEditable)

                next_register_index = registers.index[registers.index > register_row.name].min()
                if pd.isna(next_register_index):
                    field_rows = filtered_df.loc[register_row.name+1:]
                else:
                    field_rows = filtered_df.loc[register_row.name+1:next_register_index-1]

                for _, field_row in field_rows.iterrows():
                    if field_row['Registers'] != 'register':
                        field_item = QTreeWidgetItem(register_item)
                        self.set_item_values(field_item, field_row)
                        field_item.setFlags(field_item.flags() | Qt.ItemIsEditable)

            for i in range(self.tree.columnCount()):
                self.tree.resizeColumnToContents(i)

            self.update_pagination_buttons(total_registers, total_pages)
        # After updating the tree widget, update the minimap
        self.minimap.update()


    def set_item_values(self, item, row):
        for col, field in enumerate(['NAME', 'ADDR', 'Default_v_c', 'access', 'Description', 'Level', 'shadow', 'Bit']):
            item.setText(col, str(row.get(field, '')))

    def expand_all(self):
        self.tree.expandAll()

    def collapse_all(self):
        self.tree.collapseAll()

    def update_pagination_buttons(self, total_registers, total_pages):
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < total_pages)
        self.page_label.setText(f"Page {self.current_page} of {total_pages}")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_registers()

    def next_page(self):
        total_registers = len(self.df[(self.df['Book'] == self.book_selector.currentText()) &
                                      (self.df['PAGE'] == self.page_selector.currentText()) &
                                      (self.df['Registers'] == 'register')])
        total_pages = math.ceil(total_registers / self.registers_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.display_registers()
    
    def on_item_edit_started(self, item, column):
        self.is_user_edit = True
    
    def on_item_changed(self, item, column):
        if not self.is_user_edit:
            return  # Exit if change is not from user edit
        if column == 2:  # Default_v_c column
            new_value = item.text(column)
            parent = item.parent()

            if parent is None:  # This is a register
                register_item = item
                register_name = item.text(0)
                register_value = self.parse_value(new_value)

                # Update all fields under this register
                self.update_fields_ui(item, register_value)

                # Update DataFrame
                self.df.loc[self.df['NAME'] == register_name, 'Default_v_c'] = new_value

            else:  # This is a field
                register_item = parent
                register_name = register_item.text(0)
                field_name = item.text(0)

                # Get the current register value
                register_value = self.parse_value(register_item.text(column))

                # Update the field value in the register
                msb, lsb = self.parse_bit_range(item.text(1))  # Assuming 'Bit' is in column 7

                field_value = self.parse_value(new_value)
                mask = ((1 << (msb - lsb + 1)) - 1) << lsb
                register_value = (register_value & ~mask) | ((field_value << lsb) & mask)

                # Update register item
                self.tree.blockSignals(True)  # Block signals before updating
                register_item.setText(column, hex(register_value))
                self.tree.blockSignals(False)  # Unblock signals after updating

                # Update all fields UI
                self.update_fields_ui(register_item, register_value)

                # Update DataFrame
                self.df.loc[self.df['NAME'] == register_name, 'Default_v_c'] = hex(register_value)
                self.df.loc[(self.df['NAME'] == register_name) & (self.df['Description'] == field_name), 'Default_v_c'] = new_value

            # Automatically write to register (only once per change)
            self.auto_write_register(register_item)

        self.is_user_edit = False  # Reset the flag

    # def update_fields_ui(self, register_item, register_value):
    #     for i in range(register_item.childCount()):
    #         field_item = register_item.child(i)
    #         msb, lsb = self.parse_bit_range(field_item.text(1))  # Assuming 'Bit' is in column 7

    #         mask = ((1 << (msb - lsb + 1)) - 1) << lsb
    #         field_value = (register_value & mask) >> lsb
    #         field_item.setText(2, hex(field_value))  # Update 'Default_v_c' column
    
    def update_fields_ui(self, register_item, register_value):
        self.tree.blockSignals(True)  # Block signals before updating
        for i in range(register_item.childCount()):
            field_item = register_item.child(i)
            msb, lsb = self.parse_bit_range(field_item.text(1))  # Assuming 'Bit' is in column 7

            mask = ((1 << (msb - lsb + 1)) - 1) << lsb
            field_value = (register_value & mask) >> lsb
            field_item.setText(2, hex(field_value))  # Update 'Default_v_c' column
        self.tree.blockSignals(False)  # Unblock signals after updating


    def auto_write_register(self, register_item):
        addr = register_item.text(1)  # ADDR 列
        value = register_item.text(2)  # Default_v_c 列

        # 解析地址和值
        parsed_addr = self.parse_address(addr)
        parsed_value = self.parse_value(value)

        # 执行写入操作
        self.simulate_write_register(parsed_addr, parsed_value)

        print(f"Auto write: Value {hex(parsed_value)} written to address {hex(parsed_addr)}")


    def update_rw_buttons(self):
        selected_items = self.tree.selectedItems()
        if selected_items and selected_items[0].parent() is None:  # 确保选中的是寄存器，而不是字段
            self.read_button.setEnabled(True)
            self.write_button.setEnabled(True)
        else:
            self.read_button.setEnabled(False)
            self.write_button.setEnabled(False)


    def read_register(self):
        selected_item = self.tree.selectedItems()[0]
        addr = selected_item.text(1)  # ADDR 列

        # 解析地址
        parsed_addr = self.parse_address(addr)

        # 这里应该是实际的读取寄存器的代码
        # 为了演示，我们使用一个模拟的值
        read_value = self.simulate_read_register(parsed_addr)

        # 更新 Default_v_c 列
        selected_item.setText(2, hex(read_value))

        # 更新相关的 field 域
        self.update_fields(selected_item, read_value)


    def write_register(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return

        selected_item = selected_items[0]
        if selected_item.parent() is not None:
            selected_item = selected_item.parent()  # Ensure we're working with the register, not a field

        addr = selected_item.text(1)  # ADDR column
        value = selected_item.text(2)  # Default_v_c column

        # Parse address and value
        parsed_addr = self.parse_address(addr)
        parsed_value = self.parse_value(value)

        # Perform the actual write operation
        self.simulate_write_register(parsed_addr, parsed_value)

        QMessageBox.information(self, "Write Register", f"Value {hex(parsed_value)} written to address {hex(parsed_addr)}")

    def simulate_read_register(self, addr):
        # 这是一个模拟的读取函数，实际应用中应替换为真实的硬件读取操作
        return addr  # 仅作为示例，返回地址值作为读取值

    def simulate_write_register(self, addr, value):
        # 这是一个模拟的写入函数，实际应用中应替换为真实的硬件写入操作
        print(f"Writing value {hex(value)} to address {hex(addr)}")

    def parse_address(self, addr_str):
        # 移除所有空白字符
        addr_str = ''.join(addr_str.split())

        # 处理 0x 格式
        if addr_str.startswith('0x'):
            return int(addr_str, 16)

        # 处理 8'h 格式
        match = re.match(r"(\d+)'h([0-9a-fA-F]+)", addr_str)
        if match:
            width, value = match.groups()
            return int(value, 16)

        # 处理纯数字格式（假设为十六进制）
        if addr_str.isdigit():
            return int(addr_str, 16)

        # 如果都不匹配，抛出异常
        raise ValueError(f"Unsupported address format: {addr_str}")

    def parse_value(self, value_str):
        # 移除所有空白字符
        value_str = ''.join(value_str.split())

        # 处理 0x 格式
        if value_str.startswith('0x'):
            return int(value_str, 16)

        # 处理 8'h 格式
        match = re.match(r"(\d+)'h([0-9a-fA-F]+)", value_str)
        if match:
            width, value = match.groups()
            return int(value, 16)

        # 处理纯数字格式（假设为十进制）
        if value_str.isdigit():
            return int(value_str)

        # 如果都不匹配，抛出异常
        raise ValueError(f"Unsupported value format: {value_str}")


    def update_fields(self, register_item, register_value):
        for i in range(register_item.childCount()):
            field_item = register_item.child(i)
            msb, lsb = self.parse_bit_range(field_item.text(1))

            mask = ((1 << (msb - lsb + 1)) - 1) << lsb
            field_value = (register_value & mask) >> lsb
            field_item.setText(2, hex(field_value))

    def parse_bit_range(self, bit_range):
        bit_range = bit_range.strip('[]')
        if ':' in bit_range:
            msb, lsb = map(int, bit_range.split(':'))
        else:
            msb = lsb = int(bit_range)
        return msb, lsb



if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = RegisterViewer()
    viewer.show()
    sys.exit(app.exec_())