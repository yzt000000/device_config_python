import sys
from i2c_config_page import I2CConfigPage
from excel_viewer_page import ExcelViewerPage
from output_redirector import OutputRedirector
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QStyleFactory, QScrollArea, QVBoxLayout, QWidget, QTabWidget, QCheckBox
from power_switch import PowerSupplyControl  # 导入 PowerSupplyControl 类
from about import AboutPage # 导入AboutPage 
import pyvisa
from qt_material import list_themes
# 导入pprint接口，可以打印出更加漂亮的list列表数据
from pprint import pprint
from qt_material import apply_stylesheet

#pprint('总计主题样式：{} 种！'.format(len(list_themes())))
#pprint(list_themes())
#rm = pyvisa.ResourceManager('@sim')
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        #self.rm = pyvisa.ResourceManager('@sim')
        self.rm = pyvisa.ResourceManager()
        self.devices = self.auto_detect_devices()
        #self.devices = {
        #   'PVDD_device': self.rm.open_resource('GPIB0::1::INSTR'),  # 替换为控制 PVDD 的设备的资源字符串
        #   'CH_device'  : self.rm.open_resource('GPIB0::25::INSTR'),    # 替换为控制 CH1-CH4 的设备的资源字符串
        #}
        self.init_ui()


    def init_ui(self):
        layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.resize(1200, 800)

         # 创建 PowerSupplyControl 实例并添加到第一页
        # self.power_supply_control = PowerSupplyControl(self.devices)
        # self.page0 = QWidget()
        # page1_layout = QVBoxLayout()
        # page1_layout.addWidget(self.power_supply_control)
        # self.page0.setLayout(page1_layout)
        
        self.power_supply_control = PowerSupplyControl(self.devices)
        self.page0 = QWidget()
        page0_layout = QVBoxLayout()
        # 添加开关控件（QCheckBox）
        self.page0_switch = QCheckBox("Enable Power Control")
        self.page0_switch.setChecked(False)  # 默认关闭
        #self.page0_switch.setChecked(True)  # 默认关闭
        self.page0_switch.stateChanged.connect(self.toggle_page0)

        page0_layout.addWidget(self.page0_switch)
        page0_layout.addWidget(self.power_supply_control)
        self.page0.setLayout(page0_layout)




        self.page1 = I2CConfigPage(self.devices)
        self.page2 = I2CConfigPage(self.devices)
        self.excel_viewer_page = ExcelViewerPage()
        self.aboutPage = AboutPage()
        #self.excel_viewer_page.resize(1200,800) 

        # 使用 QScrollArea 包装 ExcelViewerPage
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.excel_viewer_page)

        self.tab_widget.addTab(self.page0, 'Power')
        self.tab_widget.addTab(self.page1, 'Main')
        self.tab_widget.addTab(self.page2, '临时脚本')

        self.tab_widget.addTab(self.excel_viewer_page, 'Excel 查看器')
        self.tab_widget.addTab(self.aboutPage, '软件说明')

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        self.setWindowTitle('I2C 配置工具')
        self.show()

        self.output_redirector = OutputRedirector()
        self.output_redirector.outputWritten.connect(self.page1.append_output)
        self.output_redirector.outputWritten.connect(self.page2.append_output)
        sys.stdout = self.output_redirector


    def toggle_page0(self, state):
        if state == Qt.Checked:
            # 初始化 PowerSupplyControl
            self.power_supply_control = PowerSupplyControl(self.devices)
            self.power_supply_control.init_ui()
            # 将 PowerSupplyControl 添加到 page0_layout
            self.page0.layout().addWidget(self.power_supply_control)
        else:
            # 销毁 PowerSupplyControl
            if self.power_supply_control:
                self.power_supply_control.close()
                self.power_supply_control.setParent(None)
                self.power_supply_control = None

    def auto_detect_devices(self):
        devices = {}
        resources = self.rm.list_resources()
        
        for resource in resources:
            try:
                instr = self.rm.open_resource(resource)
                try:
                    idn = instr.query('*IDN?').strip().lower()
                    if 'chroma' in idn:
                        devices['PVDD_device'] = instr
                except pyvisa.VisaIOError:
                    pass

                try:
                    idn = instr.query('ID?').strip().lower()
                    if 'hp6624a' in idn:
                        devices['CH_device'] = instr
                except pyvisa.VisaIOError:
                    pass
            except pyvisa.VisaIOError:
                pass
            # 如果未找到PVDD设备，设置为默认设备
        if 'PVDD_device' not in devices:
            #devices['PVDD_device'] = self.rm.open_resource('GPIB0::1::INSTR')
            devices['PVDD_device'] = "default_pvdd_device"

        # 如果未找到CH设备，设置为默认设备
        if 'CH_device' not in devices:
            #devices['CH_device'] =  self.rm.open_resource('GPIB0::25::INSTR')
            devices['CH_device'] =  "default_ch_device"
        return devices

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    #apply_stylesheet(app, theme='dark_teal.xml')
    #apply_stylesheet(app, theme='light_teal_500.xml')
    #app.setStyle('windowsvista')
    #app.setStyle('Windows')
    #styles = QStyleFactory.keys()
    #print("Available styles:", styles)
    #app.setStyle('WindowsXP')
    ex = MainWindow()
    sys.exit(app.exec_())
