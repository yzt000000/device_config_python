from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import QRegularExpression

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)

        self.keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'False', 'finally', 'for',
            'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'None',
            'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'True',
            'try', 'while', 'with', 'yield'
        ]

        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor('blue'))
        self.keyword_format.setFontWeight(QFont.Bold)

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor('magenta'))

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor('green'))
        self.comment_format.setFontItalic(True)

    def highlightBlock(self, text):
        for word in self.keywords:
            expression = QRegularExpression(r'\b' + word + r'\b')
            index = expression.match(text).capturedStart()
            while index != -1:
                length = expression.match(text).capturedLength()
                self.setFormat(index, length, self.keyword_format)
                index = expression.match(text, index + length).capturedStart()

        expression = QRegularExpression(r'".*?"')
        index = expression.match(text).capturedStart()
        while index != -1:
            length = expression.match(text).capturedLength()
            self.setFormat(index, length, self.string_format)
            index = expression.match(text, index + length).capturedStart()

        expression = QRegularExpression(r"'.*?'")
        index = expression.match(text).capturedStart()
        while index != -1:
            length = expression.match(text).capturedLength()
            self.setFormat(index, length, self.string_format)
            index = expression.match(text, index + length).capturedStart()

        expression = QRegularExpression(r'#.*')
        index = expression.match(text).capturedStart()
        while index != -1:
            length = expression.match(text).capturedLength()
            self.setFormat(index, length, self.comment_format)
            index = expression.match(text, index + length).capturedStart()
