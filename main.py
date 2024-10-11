import sys
import os
import time
import json
from usb_i2c import USBI2C
from i2c_config_page import I2CConfigPage
from update_status import  UpdateStatus
from excel_viewer_page import ExcelViewerPage
from output_redirector import OutputRedirector
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtWidgets import QApplication,QFileDialog, QStyleFactory, QScrollArea, QVBoxLayout, QWidget, QTabWidget, QCheckBox,QMessageBox,QLineEdit,QPushButton,QHBoxLayout,QLabel,QComboBox
from power_switch import PowerSupplyControl  # 导入 PowerSupplyControl 类
from about import AboutPage # 导入AboutPage 
import pyvisa
from qt_material import list_themes
# 导入pprint接口，可以打印出更加漂亮的list列表数据
from pprint import pprint
from qt_material import apply_stylesheet
import concurrent.futures
from license_checker import LicenseChecker


#rm = pyvisa.ResourceManager('@sim')
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.global_usb_i2c = USBI2C()
        self.global_device_address = 0x6C
        #self.rm = pyvisa.ResourceManager('@sim')

        # 检查许可证
        # 初始化 LicenseChecker
        self.checker = LicenseChecker()

        # 初始化定时器，1分钟后开始第一次许可证检查
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.initial_license_check)
        self.timer.start(300000)  # 1分钟 (60000毫秒) 的等待时间

        # 如果许可证有效，继续运行程序
        
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

        self.global_device_address_input = QComboBox(self)
        self.global_device_address_input.setFixedWidth(100)
        # 添加地址范围选项
        for i in range(0x60, 0x70):
            self.global_device_address_input.addItem(f"0x{i:02X}", i)

        # 添加特定设备选项
        self.global_device_address_input.addItem("XL008", 0x6C)
        self.global_device_address_input.addItem("XL006", 0x6A)

        update_address_button = QPushButton('更新设备地址', self)
        update_address_button.clicked.connect(self.update_global_device_address)

        # 添加I2C速度下拉菜单
        self.i2c_speed_input = QComboBox(self)
        self.i2c_speed_input.setFixedWidth(100)
        # 添加I2C速度选项
        self.i2c_speed_input.addItem("40k", 0x00)
        self.i2c_speed_input.addItem("200k", 0x01)
        self.i2c_speed_input.addItem("500k", 0x02)
        self.i2c_speed_input.addItem("800k", 0x03)

        update_speed_button = QPushButton('更新I2C速度', self)
        update_speed_button.clicked.connect(self.update_global_i2c_speed)

        # 添加导入License文件按钮
        import_license_button = QPushButton('导入License文件', self)
        import_license_button.clicked.connect(self.import_license_file)

        # 将这些控件添加到适当的布局中
        global_control_layout = QHBoxLayout()
        global_control_layout.addWidget(QLabel('全局设备地址:'))
        global_control_layout.addWidget(self.global_device_address_input)
        global_control_layout.addWidget(update_address_button)
        global_control_layout.addWidget(QLabel('I2C速度:'))
        global_control_layout.addWidget(self.i2c_speed_input)
        global_control_layout.addWidget(update_speed_button)
        global_control_layout.addWidget(import_license_button)

        # 将全局控制面板添加到主布局中
        layout.addLayout(global_control_layout)

        self.power_supply_control = PowerSupplyControl(self.devices)
        self.page0 = QWidget()
        page0_layout = QVBoxLayout()
        page0_layout.setSpacing(0)  # 设置布局中的间距为0
        page0_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为0
        # 添加开关控件（QCheckBox）
        self.page0_switch = QCheckBox("Enable Power Control")
        self.page0_switch.setChecked(False)  # 默认关闭
        self.page0_switch.stateChanged.connect(self.toggle_page0)

        
        page0_layout.addWidget(self.page0_switch)
        page0_layout.addWidget(self.power_supply_control)
        self.page0.setLayout(page0_layout)

        self.page1 = I2CConfigPage(self.devices, self.global_usb_i2c, self.global_device_address)
        self.page2 = I2CConfigPage(self.devices, self.global_usb_i2c, self.global_device_address)
        self.page3 = UpdateStatus(self.global_usb_i2c, self.global_device_address)
        self.excel_viewer_page = ExcelViewerPage(self.global_usb_i2c, self.global_device_address)
        self.aboutPage = AboutPage()

        # 使用 QScrollArea 包装 ExcelViewerPage
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.excel_viewer_page)

        self.tab_widget.addTab(self.page0, 'Power')
        self.tab_widget.addTab(self.page1, 'Main')
        self.tab_widget.addTab(self.page2, '临时脚本')
        self.tab_widget.addTab(self.page3, 'Update Status')
        self.tab_widget.addTab(self.excel_viewer_page, 'Excel 查看器')
        self.tab_widget.addTab(self.aboutPage, '软件说明')

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        self.setWindowTitle('Device Config Tool')
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

    def initial_license_check(self):
        # 第一次许可证检查
        self.timer.timeout.disconnect()  # 断开当前的信号连接

        is_valid, message = self.checker.check_license()
        if not is_valid:
            self.show_license_error(message)
            return

        # 如果许可证有效，但剩余时间小于1周，则显示警告
        if self.is_license_expiring_soon():
            self.show_license_warning(self.checker.get_time_remaining())

        # 设定定时器，每5分钟检查一次许可证
        self.timer.timeout.connect(self.start_license_checking)
        self.timer.start(30000)  # 每5分钟检查一次许可证

    def start_license_checking(self):
        # 定时检查许可证
        is_valid, message = self.checker.check_license()
        if not is_valid:
            self.show_license_error(message)
        if self.is_license_expiring_soon():
            self.show_license_warning(self.checker.get_time_remaining())

    def show_license_error(self, message):
        # 显示许可证错误的消息并退出应用程序
        QMessageBox.critical(self, "License Error", message)
        QApplication.quit()  # 退出应用程序

    def show_license_warning(self, message):
        # 显示许可证剩余时间不足一周的警告
        QMessageBox.warning(self, "License Warning", message)

    def is_license_expiring_soon(self):
        """
        检查许可证是否在一周内过期。
        """
        expiry_info = self.checker.get_time_remaining()
        if "Time remaining" in expiry_info:
            remaining_time_str = expiry_info.split("Time remaining: ")[-1].strip()
            if "days" in remaining_time_str:
                days = int(remaining_time_str.split()[0])
                return days <= 1
            else:
                return True  # 如果剩余时间中没有包含 "days"，则认为时间还充足
        return False

    # def auto_detect_devices(self):
    #     # 检查缓存
    #     cached_devices = self.load_cache()
    #     if cached_devices:
    #         return cached_devices

    #     devices = {}
    #     resources = self.rm.list_resources()

    #     with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    #         future_to_resource = {executor.submit(self.detect_device, resource): resource for resource in resources}
    #         for future in concurrent.futures.as_completed(future_to_resource):
    #             device_type, instr = future.result()
    #             if device_type:
    #                 devices[device_type] = instr

    #     # 如果未找到PVDD设备，设置为默认设备
    #     if 'PVDD_device' not in devices:
    #         devices['PVDD_device'] = "default_pvdd_device"

    #     # 如果未找到CH设备，设置为默认设备
    #     if 'CH_device' not in devices:
    #         devices['CH_device'] = "default_ch_device"

    #     # 保存缓存
    #     self.save_cache(devices)

    #     return devices

    def auto_detect_devices(self):
        # Check cache
        cached_devices = self.load_cache()
        if cached_devices:
            # Verify if cached devices are not default and still accessible
            if self.verify_cached_devices(cached_devices):
                return cached_devices

        devices = {}
        resources = self.rm.list_resources()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_resource = {executor.submit(self.detect_device, resource): resource for resource in resources}
            for future in concurrent.futures.as_completed(future_to_resource):
                device_type, instr = future.result()
                if device_type:
                    devices[device_type] = instr

        # If PVDD device is not found, set to default device
        if 'PVDD_device' not in devices:
            devices['PVDD_device'] = "default_pvdd_device"

        # If CH device is not found, set to default device
        if 'CH_device' not in devices:
            devices['CH_device'] = "default_ch_device"

        # Save cache
        self.save_cache(devices)

        return devices

    def verify_cached_devices(self, cached_devices):
        for device_type, device_address in cached_devices.items():
            if device_address in ["default_pvdd_device", "default_ch_device"]:
                return False  # If any device is default, we need to re-detect
            try:
                # Try to open the device to check if it's still accessible
                with self.rm.open_resource(device_address) as instr:
                    instr.timeout = self.timeout * 1000
                    instr.query('*IDN?')  # or 'ID?' depending on the device
            except pyvisa.VisaIOError:
                return False  # If any device is inaccessible, we need to re-detect
        return True

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
        except (json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
            self.show_error_message(f"Error loading cache: {e}")
            # 如果发生任何错误（JSON 解码错误、键错误等），我们就忽略缓存
            self.show_error_message(f"Error loading cache: {e}")
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
        except IOError as e :
            # 如果无法写入文件，我们就简单地忽略它
            self.show_error_message(f"Error saving cache: {e}")
            #pass
    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText("Error")
        msg_box.setInformativeText(message)
        msg_box.setWindowTitle("Error")
        msg_box.exec_()
    
    def update_global_device_address(self):
        try:
            new_address = self.global_device_address_input.currentData()
            self.global_device_address = new_address
            self.global_usb_i2c.update_device_address(new_address)
            print(f'全局设备地址更新为: 0x{new_address:02X}')
        except ValueError:
            QMessageBox.critical(self, '错误', '无效的设备地址')

    def update_global_i2c_speed(self):
        try:
            new_speed = self.i2c_speed_input.currentData()
            self.global_usb_i2c.update_device_speed(new_speed)
            print(f'全局I2C速度更新为: 0x{new_speed:02X}')
        except ValueError:
            QMessageBox.critical(self, '错误', '无效的I2C速度')

    def import_license_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "选择License文件", "", "License Files (*.key);;All Files (*)", options=options)
        if file_path:
            try:
                _,message = self.checker.load_license(file_path)
                #QMessageBox.information(self, "成功", "License文件导入成功")
                QMessageBox.information(self, "成功", message)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入License文件失败: {str(e)}")

    def update_all_pages_device_address(self):
        # 更新所有页面的设备地址
        self.page1.update_device_address(self.global_device_address)
        self.page2.update_device_address(self.global_device_address)
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = MainWindow()
    sys.exit(app.exec_())