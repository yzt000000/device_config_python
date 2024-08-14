import sys
import pandas as pd
import math
import re
import pickle
from usb_i2c import USBI2C

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTreeWidget, QTreeWidgetItem, QScrollArea, 
                             QInputDialog, QMessageBox, QLineEdit, QDialog, QComboBox)
from PyQt5.QtGui import QPainter, QColor, QFont , QCursor
from PyQt5.QtCore import Qt, QTimer, QPoint, QRectF

class MiniMap(QWidget):
    def __init__(self, tree_widget):
        super().__init__()
        self.tree_widget = tree_widget
        self.setFixedWidth(200)
        self.tree_widget.verticalScrollBar().valueChanged.connect(self.update)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)

        if not self.tree_widget.topLevelItemCount():
            return

        total_items = self.tree_widget.topLevelItemCount()
        visible_rect = self.tree_widget.viewport().rect()
        first_visible_item = self.tree_widget.itemAt(visible_rect.topLeft())
        last_visible_item = self.tree_widget.itemAt(visible_rect.bottomLeft())

        if not first_visible_item:
            return

        first_visible_index = self.tree_widget.indexOfTopLevelItem(first_visible_item)
        if last_visible_item:
            last_visible_index = self.tree_widget.indexOfTopLevelItem(last_visible_item)
        else:
            last_visible_index = total_items - 1

        item_height = self.height() / total_items
        visible_start = first_visible_index * item_height
        visible_end = (last_visible_index + 1) * item_height

        painter.fillRect(QRectF(0, visible_start, self.width(), visible_end - visible_start), QColor(200, 200, 255, 100))

        font = QFont()
        max_font_size = 12  # 设置最大字体大小
        font_size = max(1, int(item_height * 0.8))
        font.setPixelSize(min(font_size, max_font_size))  # 使用最小值以确保字体大小不超过上限
        painter.setFont(font)

        for i in range(total_items):
            item = self.tree_widget.topLevelItem(i)
            y = i * item_height
            text = f"{item.text(1)}: {item.text(0)}"
            if first_visible_index <= i <= last_visible_index:
                painter.setPen(Qt.blue)
            else:
                painter.setPen(Qt.black)
            painter.drawText(5, int(y + item_height * 0.9), text)  # Adjust text position to reduce vertical spacing

    def mousePressEvent(self, event):
        fraction = event.y() / self.height()
        self.tree_widget.verticalScrollBar().setValue(int(fraction * self.tree_widget.verticalScrollBar().maximum()))
        self.update()
