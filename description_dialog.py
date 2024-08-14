from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel

class DescriptionDialog(QDialog):
    def __init__(self, description, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Description 详情')
        self.setModal(False)  # 设置为非模态对话框

        layout = QVBoxLayout()
        self.description_label = QLabel(description)
        layout.addWidget(self.description_label)
        self.setLayout(layout)
