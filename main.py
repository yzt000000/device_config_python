import sys
import os
import time
import json
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
import concurrent.futures


#rm = pyvisa.ResourceManager('@sim')
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        #self.rm = pyvisa.ResourceManager('@sim')
        
        # 添加这些行
        self.cache_file = 'device_cache.json'
        self.cache_expiry = 3600  # 缓存有效期1小时
        self.timeout = 2  # 设置2秒超时
        try:
            self.rm = pyvisa.ResourceManager()
        except:
            self.rm = pyvisa.ResourceManager('@sim')

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

    # def auto_detect_devices(self):
    #     devices = {}
    #     resources = self.rm.list_resources()
    #     self.timeout = 2  # 设置2秒超时
    #     self.cache_file = 'device_cache.json'
    #     self.cache_expiry = 3600  # 缓存有效期1小时
        
    #     for resource in resources:
    #         try:
    #             instr = self.rm.open_resource(resource)
    #             try:
    #                 idn = instr.query('*IDN?').strip().lower()
    #                 if 'chroma' in idn:
    #                     devices['PVDD_device'] = instr
    #             except pyvisa.VisaIOError:
    #                 pass

    #             try:
    #                 idn = instr.query('ID?').strip().lower()
    #                 if 'hp6624a' in idn:
    #                     devices['CH_device'] = instr
    #             except pyvisa.VisaIOError:
    #                 pass
    #         except pyvisa.VisaIOError:
    #             pass
    #         # 如果未找到PVDD设备，设置为默认设备
    #     if 'PVDD_device' not in devices:
    #         #devices['PVDD_device'] = self.rm.open_resource('GPIB0::1::INSTR')
    #         devices['PVDD_device'] = "default_pvdd_device"

    #     # 如果未找到CH设备，设置为默认设备
    #     if 'CH_device' not in devices:
    #         #devices['CH_device'] =  self.rm.open_resource('GPIB0::25::INSTR')
    #         devices['CH_device'] =  "default_ch_device"
    #     return devices
    

    def auto_detect_devices(self):
        # 检查缓存
        cached_devices = self.load_cache()
        if cached_devices:
            return cached_devices

        devices = {}
        resources = self.rm.list_resources()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_resource = {executor.submit(self.detect_device, resource): resource for resource in resources}
            for future in concurrent.futures.as_completed(future_to_resource):
                device_type, instr = future.result()
                if device_type:
                    devices[device_type] = instr

        # 如果未找到PVDD设备，设置为默认设备
        if 'PVDD_device' not in devices:
            devices['PVDD_device'] = "default_pvdd_device"

        # 如果未找到CH设备，设置为默认设备
        if 'CH_device' not in devices:
            devices['CH_device'] = "default_ch_device"

        # 保存缓存
        self.save_cache(devices)

        return devices

    def detect_device(self, resource):
        try:
            with self.rm.open_resource(resource) as instr:
                instr.timeout = self.timeout * 1000  # pyvisa使用毫秒

                # 尝试 '*IDN?' 查询
                try:
                    idn = instr.query('*IDN?').strip().lower()
                    if 'chroma' in idn:
                        return 'PVDD_device', instr
                except pyvisa.VisaIOError:
                    pass

                # 尝试 'ID?' 查询
                try:
                    idn = instr.query('ID?').strip().lower()
                    if 'hp6624a' in idn:
                        return 'CH_device', instr
                except pyvisa.VisaIOError:
                    pass

        except pyvisa.VisaIOError:
            pass

        return None, None

    def load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    content = f.read().strip()
                    if content:  # 检查文件是否为空
                        cache_data = json.loads(content)
                        if time.time() - cache_data.get('timestamp', 0) < self.cache_expiry:
                            return cache_data.get('devices')
        except (json.JSONDecodeError, ValueError, KeyError, TypeError):
            # 如果发生任何错误（JSON 解码错误、键错误等），我们就忽略缓存
            pass
        
        # 如果出现任何问题，或缓存过期，就返回 None
        return None

    def save_cache(self, devices):
        cache_data = {
            'timestamp': time.time(),
            'devices': {k: str(v) for k, v in devices.items()}  # 将设备对象转换为字符串
        }
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
        except IOError:
            # 如果无法写入文件，我们就简单地忽略它
            pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = MainWindow()
    sys.exit(app.exec_())
