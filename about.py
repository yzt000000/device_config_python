import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QTextBrowser
from PyQt5.QtGui import QFont
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("富文本示例 - 带语法高亮")
        self.text_browser = QTextBrowser(self)
        self.text_browser.setOpenExternalLinks(True)
        
        self.set_rich_text_content()
        
        layout = QVBoxLayout()
        layout.addWidget(self.text_browser)
        self.setLayout(layout)

    def highlight_code(self, code, language='python'):
        lexer = PythonLexer()
        formatter = HtmlFormatter(style='default')  # 使用默认风格
        highlighted_code = highlight(code, lexer, formatter)
        # 修改背景色和文字色
        style_defs = formatter.get_style_defs('.highlight')
        style_defs = style_defs.replace('background-color: #f5f5f5;', 'background-color: #ffffff;')
        style_defs = style_defs.replace('color: #000000;', 'color: #000000;')  # 修改文本颜色
        style_defs = style_defs.replace('color: #0000ff;', 'color: #0000ff;')  # 修改关键字颜色
        style_defs = style_defs.replace('color: #a31515;', 'color: #a31515;')  # 修改字符串颜色
        style_defs = style_defs.replace('color: #008000;', 'color: #008000;')  # 修改注释颜色
        return highlighted_code, style_defs

    def set_rich_text_content(self):
        # 内置函数
        python_code = """
time.sleep(0.1)
read_i2c(0x00)
write_i2c(0x01, 0xAA)
power_control.set_slew_rate("PVDD", 10)       #10v/ms
power_control.set_voltage("PVDD", 20.0)       #20V
power_control.toggle_power_func("CH1","ON")   # power on
power_control.toggle_power_func("CH2","OFF")  # power off
power_control.set_max_voltage("PVDD",30.0)    # voltage limit 
power_control.set_current("PVDD",1.0)         # set current limit to 1A

#for loop , adjust PVDD
for i in range(10):
    power_control.set_slew_rate("PVDD", 1000)
    time.sleep(5)
    power_control.set_voltage("PVDD", 200)

    time.sleep(5)
    power_control.set_slew_rate("PVDD", 500)
    time.sleep(5)
    power_control.set_voltage("PVDD", 0)
    time.sleep(5)

"""

        highlighted_code, style_defs = self.highlight_code(python_code)

        content = f"""
<h1 style="color: #1a5f7a;">软件说明：</h1>

<p>1. Power switch 控制 chroma 和 hp6624a 电源</p>
<p>2. Main/临时脚本 支持寄存器读写，脚本执行，脚本load，save，中断，继续，终止； 支持log的清除和保存\n</p>
<p>3. excel 查看器 提供xl008_2p0 寄存器描述，寄存器配置，page 切换，缩略图等\n</p>


<h2 style="color: #197278;">内建函数实例</h2>

<style>
{style_defs}
.highlight {{
    background-color: #ffffff;  /* 确保背景色为白色 */
    padding: 10px;
    border-radius: 5px;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.4;
}}
</style>

{highlighted_code}
"""

#<p>上面的代码使用 Pygments 库实现了语法高亮。</p>

#<h2 style="color: #197278;">其他富文本示例</h2>

#<ul>
#    <li><strong>粗体文本</strong></li>
#    <li><em>斜体文本</em></li>
#    <li><span style="color: #ff0000;">红色文本</span></li>
#    <li><span style="background-color: #ffff00; color: #000000;">黄色背景黑色文本</span></li>
#</ul>

#<blockquote style="border-left: 4px solid #ccc; padding-left: 10px; color: #555;">
#这是一个引用示例，展示了如何与语法高亮的代码块结合使用。
#</blockquote>
#        """
        
        self.text_browser.setHtml(content)
        
        # 设置整体字体
        font = QFont("Arial", 11)
        self.text_browser.setFont(font)
        
        # 设置样式
        self.text_browser.document().setDefaultStyleSheet("""
            body { line-height: 1.6; }
            h1 { font-size: 24pt; margin-bottom: 20px; }
            h2 { font-size: 18pt; margin-top: 20px; margin-bottom: 10px; }
        """)


