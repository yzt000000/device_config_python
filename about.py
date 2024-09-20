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
################# I2C #####################################
read_i2c(0x00)
write_i2c(0x01, 0xAA)
read_i2c_disp(0x00)
write_i2c_disp(0x01,0xAA)
###############  UART #####################################

# 发送UART数据
write_uart("48 65 6C 6C 6F 20 53 65 72 69 61 6C 20 50 6F 72 74 21")  # 发送 "Hello Serial Port!"
write_uart("04 05 A5 00 A5 00 94 03")

# 读取UART数据
received_data = read_uart(timeout=2, num_bytes=1024)  # 2秒超时，最多读取1024字节
if received_data:
    print(f"读取到的数据: {received_data}")
#POWER


# 使用循环发送和接收数据
for i in range(5):
    write_uart(f"4D 65 73 73 61 67 65 20 {i:02X}")  # 发送 "Message X"，其中X是循环计数
    time.sleep(0.5)  # 等待0.5秒
    received = uart_read(timeout=1)
    if received:
        print(f"循环 {i+1}: 接收到 {received}")
    else:
        print(f"循环 {i+1}: 未接收到数据")

##################### 电源 ###############################
# 开关电源
open_devices.open_devices()
power_control.toggle_power_func("CH1", "ON")   # 打开CH1
power_control.toggle_power_func("CH2", "OFF")  # 关闭CH2

# 设置最大电压
power_control.set_max_voltage("PVDD", 30.0)    # 设置PVDD最大电压为30V

# 设置电流保护和限制
power_control.set_current_prot("PVDD", 10.0)   # 设置PVDD电流保护为10A
power_control.set_current_limit("PVDD", 10.0)  # 设置PVDD电流限制为10A

# 设置压摆率（斜率）
power_control.set_slew_rate("PVDD", 10)        # 设置PVDD压摆率为10V/ms

# 读取电压、电流和功率
voltage = power_control.read_voltage("CH1")
current = power_control.read_current("CH1")
power = power_control.read_power("CH1")
print(f"CH1 - 电压: {voltage}V, 电流: {current}A, 功率: {power}W")

# 使用循环调整PVDD电压
for voltage in range(0, 21, 5):
    power_control.set_voltage("PVDD", voltage)
    time.sleep(1)
    measured_voltage = power_control.read_voltage("PVDD")
    print(f"设置PVDD电压为{voltage}V，测量值为{measured_voltage}V")
############################## Print ###########################################
#Print
# 绿色文本
print('<span style="color: green;">这是一段绿色文本</span>')
# 蓝色粗体文本
print('<span style="color: blue; font-weight: bold;">这是一段蓝色粗体文本</span>')
# 红色斜体文本
print('<span style="color: red; font-style: italic;">这是一段红色斜体文本</span>')
# 黑色带下划线文本
print('<span style="color: black; text-decoration: underline;">这是一段黑色带下划线的文本</span>')
# 粉色背景色的文本
print('<span style="background-color: pink;">这段文本有粉色背景</span>')
# 大号字体文本
print('<span style="font-size: 20px;">这段文本的字体大小为20px</span>')
# 小号字体文本
print('<span style="font-size: 10px;">这段文本的字体大小为10px</span>')
# 大号加粗斜体文本
print('<span style="font-size: 24px; font-weight: bold; font-style: italic;">这段文本的字体大小为24px，且加粗和斜体</span>')

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


