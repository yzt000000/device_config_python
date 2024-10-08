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
data = write_uart("48 65 6C 6C 6F 20 53 65 72 69 61 6C 20 50 6F 72 74 21")  # 发送 "Hello Serial Port!"
data = write_uart("04 05 A5 00 A5 00 94 03")
data = write_uart("01 05 A5 00 A5 00 94 56")

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
############################## APX #############################################
import sys, clr  #导入库

clr.AddReference("System.Drawing")              
clr.AddReference("System.Windows.Forms")
# Add a reference to the APx API        
clr.AddReference(r"C:\Program Files\Audio Precision\APx500 4.5\API\AudioPrecision.API2.dll")    #AP路径
clr.AddReference(r"C:\Program Files\Audio Precision\APx500 4.5\API\AudioPrecision.API.dll") 

from AudioPrecision.API import *    #导入API
from System.Drawing import Point
from System.Windows.Forms import Application, Button, Form, Label
from System.IO import Directory, Path

APx = APx500_Application()  #启动AP
APx.Visible = True  #可视化，打开软件页面

APx.OperatingMode = APxOperatingMode.BenchMode;   #切换模式
#APx.OperatingMode = APxOperatingMode.SequenceMode;   #切换模式

APx.BenchMode.Setup.OutputConnector.Type = OutputConnectorType.DigitalSerial #切换输出类型  DigitalSerial/DigitalOptical/AnalogBalanced等

############ SerialDigitalTransmitter #########
APx.BenchMode.Setup.SerialDigitalTransmitter.Format = SerialFormat.Custom #输出格式切换至Custom
APx.BenchMode.Setup.SerialDigitalTransmitter.BitClkSendEdgeSync = EdgeSync.FallingEdge  #Bclock 下降沿对齐
#APx.BenchMode.Setup.SerialDigitalTransmitter.BitClkSendEdgeSync = EdgeSync.RisingEdge  #Bclock 上升沿对齐
APx.BenchMode.Setup.SerialDigitalTransmitter.BitDepth = 24  #有效位
#APx.BenchMode.Setup.SerialDigitalTransmitter.Dither = False #dither 开关  =True 打开
APx.BenchMode.Setup.SerialDigitalTransmitter.BitFrameClockDirection = ClockDirection.Out #
APx.BenchMode.Setup.SerialDigitalTransmitter.Channels = SerialChannels.Eight  #输出通道数量
APx.BenchMode.Setup.SerialDigitalTransmitter.DataJustification = SerialCustomDataJustification.LeftJustified #对齐方式
#APx.BenchMode.Setup.SerialDigitalTransmitter.Format = SerialFormat.I2S #输出格式切换I2S
APx.BenchMode.Setup.SerialDigitalTransmitter.FrameClockInvert = False #FrameClockInvert开
APx.BenchMode.Setup.SerialDigitalTransmitter.FrameClockLeftOneBit  = True #空一位对齐
APx.BenchMode.Setup.SerialDigitalTransmitter.FrameClockPulseWidth = FrameClockPulseWidth.OneBitClock #Fclock宽度
APx.BenchMode.Setup.SerialDigitalTransmitter.InvertMasterClock = False #Mclock翻转开关
APx.BenchMode.Setup.SerialDigitalTransmitter.LogicLevel = SerialLogicLevel.V3p3 #逻辑电平值 支持1.8 2.5 3.3
APx.BenchMode.Setup.SerialDigitalTransmitter.MasterClockMultiplier = 256  #Mclk/Fclk  ratio
APx.BenchMode.Setup.SerialDigitalTransmitter.MasterClockOff = False #mclk开关
APx.BenchMode.Setup.SerialDigitalTransmitter.MasterClockSource = MasterClockSource.Internal #mclk源自内部外部
APx.BenchMode.Setup.SerialDigitalTransmitter.MsbFirst = True
APx.BenchMode.Setup.SerialDigitalTransmitter.SampleRate.Value = 48000  #输出采样率
APx.BenchMode.Setup.SerialDigitalTransmitter.SingleDataLine = True  #single data line  即TDM
APx.BenchMode.Setup.SerialDigitalTransmitter.WordWidth = 32  #位宽
APx.BenchMode.Setup.SerialDigitalTransmitter.EnableOutputs = True #打开SerialDigital输出

APx.BenchMode.Setup.InputConnector.Type = InputConnectorType.AnalogBalanced    #切换输入类型
APx.BenchMode.Setup.AnalogInput.ChannelCount = 2 #输入通道数量

########## HIGH PASS FILTER ##################
APx.BenchMode.Setup.HighpassFilter = HighpassFilterMode.Butterworth #高通滤波器类型
#APx.BenchMode.Setup.HighpassFilter = HighpassFilterMode.AC
APx.BenchMode.Setup.HighpassFilterFrequency = 10   #高通滤波器频率

########## LOW PASS FILTER ##################
APx.BenchMode.Setup.LowpassFilterAnalog = LowpassFilterModeAnalog.Butterworth #低通滤波器类型
APx.BenchMode.Setup.LowpassFilterFrequencyAnalog = 22400 #低通滤波器频率

########## Weighting type ##################
#APx.BenchMode.Setup.WeightingFilter = SignalPathWeightingFilterType.wt_None 
#APx.BenchMode.Setup.WeightingFilter = SignalPathWeightingFilterType.wt_A
#APx.BenchMode.Setup.WeightingFilter = SignalPathWeightingFilterType.wt_Deemph50us

######### References ################
#APx.BenchMode.Setup.References.AnalogInputReferences.dBrA.Value #设置dBrA的值
APx.BenchMode.Setup.References.AnalogInputReferences.Watts.Value = 4  #设置负载阻值

########## switcher ##############
APx.BenchMode.Setup.UseInputSwitcher = True #enable switcher
#APx.BenchMode.Setup.UseInputSwitcher = False #disable switcher
APx.BenchMode.Setup.InputSwitcherConfiguration.SetChannelA(SwitcherAddress.Switcher0, SwitcherChannelSelection.Ch1)
#APx.BenchMode.Setup.InputSwitcherConfiguration.SetChannelA(SwitcherAddress.Switcher0, SwitcherChannelSelection.Ch2)
#APx.BenchMode.Setup.InputSwitcherConfiguration.SetChannelA(SwitcherAddress.Switcher0, SwitcherChannelSelection.Ch3)
#APx.BenchMode.Setup.InputSwitcherConfiguration.SetChannelA(SwitcherAddress.Switcher0, SwitcherChannelSelection.Ch4)  #Switcher切换CHA

#APx.BenchMode.Setup.InputSwitcherConfiguration.SetChannelB(SwitcherAddress.Switcher0, SwitcherChannelSelection.Ch1)
#APx.BenchMode.Setup.InputSwitcherConfiguration.SetChannelB(SwitcherAddress.Switcher0, SwitcherChannelSelection.Ch2)
APx.BenchMode.Setup.InputSwitcherConfiguration.SetChannelB(SwitcherAddress.Switcher0, SwitcherChannelSelection.Ch3)
#APx.BenchMode.Setup.InputSwitcherConfiguration.SetChannelB(SwitcherAddress.Switcher0, SwitcherChannelSelection.Ch4)  #Switcher切换CHB

######### Generator ##############
APx.BenchMode.Generator.AutoOn = True #AutoOn 开关
APx.BenchMode.Generator.Frequency.Value = 1000 #频率设置
APx.BenchMode.Generator.Waveform = 'Sine'  #更改波形
### IMD ###
#APx.BenchMode.Generator.Imd.Frequency1.Value = 60  #F1
#APx.BenchMode.Generator.Imd.Frequency2.Value = 7000  #F2
#APx.BenchMode.Generator.Imd.SignalType = ImdGeneratorSignalType.Smpte4To1  #信号类型
#APx.BenchMode.Generator.Imd.Split = False # split 关
###########
APx.BenchMode.Generator.Levels.Unit = 'dBFS'  #单位
APx.BenchMode.Generator.Levels.TrackFirstChannel = True  #跟随一通道
APx.BenchMode.Generator.Levels.SetValue(OutputChannelIndex.Ch1, -20)   #改变输出幅度
#APx.BenchMode.Generator.On = True   #输出开启

##############  sweep  ####################
APx.BenchMode.Measurements.SteppedSweep.Append = True  #append graph data开
APx.BenchMode.Measurements.SteppedSweep.Repeat = False  #  repeat开关
APx.BenchMode.Measurements.SteppedSweep.Source = SweepSourceParameterType.GeneratorFrequency #扫频
APx.BenchMode.Measurements.SteppedSweep.SourceParameters.Start.Value = 20000 #开始频率
APx.BenchMode.Measurements.SteppedSweep.SourceParameters.Stop.Value = 20  # 结束频率
#APx.BenchMode.Measurements.SteppedSweep.SourceParameters.StepSize.Value
APx.BenchMode.Measurements.SteppedSweep.SourceParameters.NumberOfPoints = 51  #point数量
APx.BenchMode.Measurements.SteppedSweep.Graphs.Add('THD+NRatio').Result  #增加测试项
#APx.BenchMode.Measurements.SteppedSweep.Graphs.Delete('Gain')   #删除测试项
#APx.BenchMode.Measurements.SteppedSweep.ClearData() #清除所有测试数据
#APx.BenchMode.Measurements.SteppedSweep.ClearData(SourceDataType.Measured, dataIndex=1) #清除某一个测试数据
#APx.BenchMode.Measurements.SteppedSweep.ExportData('test1', NumberOfGraphPoints.GraphPointsSameAsGraph, appendIfExists)  #导出数据
#APx.BenchMode.Measurements.SteppedSweep.ExportData('test1',) #导出数据
APx.BenchMode.Measurements.SteppedSweep.Start() #测试开始
#APx.BenchMode.Measurements.SteppedSweep.Stop()  #测试中断
#APx.BenchMode.Measurements.SteppedSweep.Source = SweepSourceParameterType.GeneratorLevel
#APx.BenchMode.Measurements.SteppedSweep.SourceParameters.Start.Value
############################## DMM ###########################################
def __init__(self):
def _find_dmm_resource(self):
def _open_device(self, resourceName=""):
def _show_instrument_message(self):
def _reset_dmm(self):
def _read_config(self):
def _set_config(self, Measurementype, Range="DEF", Resolution="DEF"):
def _config_current_parameter(self, Measurementype, Range="DEF", Resolution="DEF"):
def _measuremen_diode(self):
def _measuremen_frequency_or_period(self, Measurementype, Range="DEF", Resolution="DEF"):
def _measuremen_resistance_or_fresistance(self, Measurementype, Range="DEF", Resolution="DEF"):
def _config_voltage_parameter(self, Measurementype, Range="DEF", Resolution="DEF"):
def _check_terminals(self, Terminals):
def _sample(self):
def _read_buff(self):
def _finish(self):
def _save_buff_to_csv(self, logpath):
def _dmm_display(self, displayStr):
def _dmm_display_clear(self):
def _dmm_display_view(self, ViewType):
def _set_limit(self, Limit_Low, Limit_Upp):
def _limit_clear(self):
def _set_limit_on_off(self, SetLimitONOFF="OFF"):
def _read_questionable(self):
def _set_trigger_source(self, Source):
def _set_sample_count(self, Count):
def _voltage_measuremen(self, VoltageType, Count=50, Range="DEF", Resolution="DEF", LimitLow=0, LimitUpp=0):
def _current_measuremen(self, CurrentType, Count=50, Range="DEF", Resolution="DEF"):
def connect_and_measure(self, resourceName=""):
###############################################################
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


