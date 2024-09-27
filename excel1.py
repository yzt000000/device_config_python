import sys
import math
import re
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, 
                             QComboBox, QPushButton, QFileDialog, QHBoxLayout, QHeaderView, QLabel, QMessageBox, 
                             QDialog, QTextEdit, QScrollBar, QSplitter)
from PyQt5.QtCore import Qt, QEvent, QTimer, QRectF
from PyQt5.QtGui import QCursor, QPainter, QColor, QPen, QFont

class MiniMapWidget(QWidget):
    def __init__(self, tree_widget, parent=None):
        super().__init__(parent)
        self.tree_widget = tree_widget
        self.setFixedWidth(200)  # 设置缩略图宽度
        self.tree_widget.verticalScrollBar().valueChanged.connect(self.update)  # 连接滚动条信号更新缩略图

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)  # 填充背景为白色

        total_items = self.tree_widget.topLevelItemCount()
        if total_items == 0:
            return  # 如果没有寄存器项目，直接返回

        # 获取树控件中可见区域
        visible_rect = self.tree_widget.viewport().rect()
        first_visible_item = self.tree_widget.itemAt(visible_rect.topLeft())  # 第一个可见项目
        last_visible_item = self.tree_widget.itemAt(visible_rect.bottomLeft())  # 最后一个可见项目

        if not first_visible_item:
            return  # 如果没有可见项目，直接返回

        # 计算第一个和最后一个可见寄存器的索引
        first_visible_index = self.tree_widget.indexOfTopLevelItem(first_visible_item)
        last_visible_index = self.tree_widget.indexOfTopLevelItem(last_visible_item) if last_visible_item else total_items - 1

        # 计算每个寄存器在缩略图中的高度
        item_height = self.height() / total_items
        visible_start = first_visible_index * item_height  # 可见区域起始
        visible_end = (last_visible_index + 1) * item_height  # 可见区域结束

        # 绘制当前可见的区域
        painter.fillRect(QRectF(0, visible_start, self.width(), visible_end - visible_start), QColor(200, 200, 255, 100))

        # 设置字体
        font = QFont()
        max_font_size = 12  # 最大字体大小
        font_size = max(1, int(item_height * 0.8))  # 动态计算字体大小
        font.setPixelSize(min(font_size, max_font_size))  # 确保字体不会超出上限
        painter.setFont(font)

        # 遍历所有寄存器项目并绘制寄存器名字
        for i in range(total_items):
            item = self.tree_widget.topLevelItem(i)
            y = i * item_height  # 计算每个寄存器的垂直位置
            text = f"{item.text(1)}: {item.text(0)}"  # 假设寄存器的名字在第一列和第二列

            # 根据是否在可见区域中设置不同的颜色
            if first_visible_index <= i <= last_visible_index:
                painter.setPen(Qt.blue)  # 蓝色表示当前可见项目
            else:
                painter.setPen(Qt.black)  # 黑色表示不可见项目

            # 绘制寄存器名字
            painter.drawText(5, int(y + item_height * 0.9), text)  # 调整文本位置以减少垂直间距

    def mousePressEvent(self, event):
        # 计算点击位置相对于总高度的比例
        fraction = event.y() / self.height()
        # 根据比例调整树控件的滚动条位置
        self.tree_widget.verticalScrollBar().setValue(int(fraction * self.tree_widget.verticalScrollBar().maximum()))
        self.update()  # 更新缩略图显示




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

        # 创建一个新的布局来容纳顶部的按钮和选择器
        self.top_layout = QHBoxLayout()
        self.top_layout.setContentsMargins(0, 0, 0, 0)  # 设置边距为0
        self.top_layout.setSpacing(5)  # 设置组件之间的间距

        # 添加寄存器读写按钮
        self.read_button = QPushButton("Read Register")
        self.write_button = QPushButton("Write Register")
        self.read_button.clicked.connect(self.read_register)
        self.write_button.clicked.connect(self.write_register)
        self.top_layout.addWidget(self.read_button)
        self.top_layout.addWidget(self.write_button)

        # 添加 BOOK 选择器
        self.book_label = QLabel("BOOK:")
        self.book_label.setFixedWidth(30)  # 指定 book_label 宽度
        self.book_selector = QComboBox()
        self.book_selector.setFixedWidth(50)  # 指定 book_selector 宽度
        self.top_layout.addWidget(self.book_label)
        self.top_layout.addWidget(self.book_selector)

        # 添加 PAGE 选择器
        self.page_label = QLabel("PAGE:")
        self.page_label.setFixedWidth(30)  # 指定 page_label 宽度
        self.page_selector = QComboBox()
        self.page_selector.setFixedWidth(50)  # 指定 page_selector 宽度
        self.top_layout.addWidget(self.page_label)
        self.top_layout.addWidget(self.page_selector)

        # 添加 Load Excel File 按钮
        self.load_button = QPushButton("Load Excel File")
        self.load_button.clicked.connect(self.load_excel)
        self.top_layout.addWidget(self.load_button)

        # 添加 Previous 和 Next 按钮
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)
        self.top_layout.addWidget(self.prev_button)
        self.top_layout.addWidget(self.next_button)

        # 添加 Expand All 按钮
        self.expand_button = QPushButton("Expand All")
        self.expand_button.clicked.connect(self.expand_all)
        self.top_layout.addWidget(self.expand_button)

        # 添加 Collapse All 按钮
        self.collapse_button = QPushButton("Collapse All")
        self.collapse_button.clicked.connect(self.collapse_all)
        self.top_layout.addWidget(self.collapse_button)

        # 添加 Page Label
        self.page_label = QLabel()
        self.top_layout.addWidget(self.page_label)

        # 将顶部布局添加到主布局中，并设置为固定高度
        top_widget = QWidget()
        top_widget.setLayout(self.top_layout)
        top_widget.setFixedHeight(40)  # 设置固定高度，可以根据需要调整
        self.layout.addWidget(top_widget)

        self.file_path_layout = QHBoxLayout()

        # 添加 Excel 文件路径的标签
        self.file_path_label = QLabel("Loaded file: ")
        self.file_path_label.setFixedWidth(40)  # 指定 page_label 宽度
        self.file_path_value = QLabel("")  # 初始时为空，加载文件后更新

        # 将标签和显示路径的 QLabel 添加到布局中
        self.file_path_layout.addWidget(self.file_path_label)
        self.file_path_layout.addWidget(self.file_path_value)

        # 创建一个 QWidget 来包含 file_path_layout
        file_path_widget = QWidget()
        file_path_widget.setLayout(self.file_path_layout)
        file_path_widget.setFixedHeight(30)  # 设置固定高度，比如 30 像素

        # 将 file_path_widget 添加到主布局中
        self.layout.addWidget(file_path_widget)


        # 创建水平布局来容纳树形控件和minimap
        splitter = QSplitter(Qt.Horizontal)
        # 添加树形控件
        self.tree = EditableTreeWidget(self)
        self.tree.setHeaderLabels(["NAME", "ADDR", "Default_v_c", "access", "Description", "Level"])
        self.tree.itemChanged.connect(self.on_item_changed)
        splitter.addWidget(self.tree)

        # 创建并添加minimap
        self.minimap = MiniMapWidget(self.tree)
        splitter.addWidget(self.minimap)
        # 设置splitter的初始大小
        splitter.setSizes([1000, 100])  # 树形控件占大部分宽度，minimap占较小部分

        # 将splitter添加到主布局中
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
        self.registers_per_page = 50


    # def load_excel(self):
    #     file_name, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx *.xls)")
    #     if file_name:
    #         self.file_path_value.setText(file_name)  # 更新路径显示
    #         self.df = pd.read_excel(file_name, sheet_name='regmap')
    #         self.df = self.df.fillna('')
    #         self.df['Book'] = self.df['Book'].apply(hex_format)
    #         self.df['PAGE'] = self.df['PAGE'].apply(hex_format)
    #         self.update_book_selector()
    
    def load_excel(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Excel or Pickle File", "", "Excel or Pickle Files (*.xlsx *.xls *.pkl)")
        if file_name:
            self.file_path_value.setText(file_name)  # 更新路径显示
            if file_name.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(file_name, sheet_name='regmap')
                # 生成同名的 pkl 文件
                pkl_file_name = f"{file_name.rsplit('.', 1)[0]}.pkl"
                self.df.to_pickle(pkl_file_name)  # 保存为 pkl 文件
            elif file_name.endswith('.pkl'):
                self.df = pd.read_pickle(file_name)
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
        for col, field in enumerate(['NAME', 'ADDR', 'Default_v_c', 'access', 'Description', 'Level']):
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