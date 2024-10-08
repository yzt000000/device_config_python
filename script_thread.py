from PyQt5.QtCore import QThread, pyqtSignal
import sys
import io
import threading
import traceback
import time

class ScriptThread(QThread):
    output = pyqtSignal(str)
    paused = pyqtSignal()
    resumed = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, script, read_func, write_func,power_switch_function,dmm,uart_read_func,uart_write_func,i2c_read_disp_func,i2c_write_disp_func):
        super().__init__()
        self.script = script
        self.read_func = self.wrap_function(read_func)
        self.write_func = self.wrap_function(write_func)
        self.uart_write_func = self.wrap_function(uart_write_func)
        self.uart_read_func = self.wrap_function(uart_read_func)
        self.i2c_read_disp_func = self.wrap_function(i2c_read_disp_func)
        self.i2c_write_disp_func = self.wrap_function(i2c_write_disp_func)
        self.power_switch_function = power_switch_function
        self.dmm = dmm
        self.is_paused = False
        self.should_exit = False
        self.pause_lock = threading.Lock()
        self.pause_cond = threading.Condition(self.pause_lock)

    def run(self):
        old_stdout = None  # 确保 old_stdout 变量在任何情况下都能被访问
        new_stdout = None  # 确保 new_stdout 变量在任何情况下都能被访问
        try:
            globals_dict = {
                'read_i2c': self.read_func,
                'write_i2c': self.write_func,
                'write_uart': self.uart_write_func,
                'read_uart': self.uart_read_func,
                'read_i2c_disp' : self.i2c_read_disp_func,
                'write_i2c_disp' : self.i2c_write_disp_func,
                'power_control': self.power_switch_function,
                'dmm' : self.dmm,
                'print': self.custom_print,
                'time': time  # Add time module for sleep function

            }
            locals_dict = {}

            # 重定向标准输出
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout

            exec(self.script, globals_dict, locals_dict)
        except SystemExit:
            self.output.emit("脚本执行被用户终止\n")
        except Exception as e:
            error_msg = f'<span style="color: red;">Error: {str(e)}</span>'
            self.output.emit(error_msg)
        finally:
            # 恢复标准输出
            if old_stdout is not None:
                sys.stdout = old_stdout
            if new_stdout is not None:
                output = new_stdout.getvalue()
                if output:
                    self.output.emit(output)
            self.finished.emit()

    def wrap_function(self, func):
        def wrapper(*args, **kwargs):
            self.check_pause()
            return func(*args, **kwargs)
        return wrapper

    def check_pause(self):
        if self.is_paused:
            self.paused.emit()
            with self.pause_cond:
                while self.is_paused and not self.should_exit:
                    self.pause_cond.wait()
            if self.should_exit:
                raise SystemExit("脚本执行被用户终止")
            else:
                self.resumed.emit()
        elif self.should_exit:
            raise SystemExit("脚本执行被用户终止")

    def custom_print(self, *args, **kwargs):
        self.check_pause()
        output = " ".join(map(str, args))
        self.output.emit(output + "\n")

    def interrupt(self):
        with self.pause_lock:
            self.is_paused = True

    def resume(self):
        with self.pause_lock:
            self.is_paused = False
            self.pause_cond.notify_all()

    def exit(self):
        with self.pause_lock:
            self.should_exit = True
            self.is_paused = False
            self.pause_cond.notify_all()

 
