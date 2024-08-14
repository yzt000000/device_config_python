from PyQt5.QtCore import pyqtSignal, QObject

class OutputRedirector(QObject):
    outputWritten = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._buffer = ''

    def write(self, text):
        self._buffer += text
        self.outputWritten.emit(text)

    def flush(self):
        pass
