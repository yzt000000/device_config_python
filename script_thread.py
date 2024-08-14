
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import threading
import traceback
import time

class ScriptThread(QThread):
    output = pyqtSignal(str)
    paused = pyqtSignal()
    resumed = pyqtSignal()

    def __init__(self, script, read_func, write_func, power_switch_function):
        super().__init__()
        self.script = script
        self.read_func = self.wrap_function(read_func)
        self.write_func = self.wrap_function(write_func)
        self.power_switch_function = power_switch_function
        self.is_paused = False
        self.should_exit = False
        self.pause_lock = threading.Lock()
        self.pause_cond = threading.Condition(self.pause_lock)


    
    def run(self):
        try:
            exec_globals = {
                'read_i2c': self.read_func,
                'write_i2c': self.write_func,
                'power_control': self.power_switch_function,
                'print': self.custom_print,
                'time': time,  # Add time module for sleep function
                'print_colored': self.print_colored  # Add print_colored function
            }
            #self.output.emit(f"绑定的 toggle_power_test 方法: {exec_globals['toggle_power_test']}\n")
            exec(self.script, exec_globals)
        except SystemExit:
            self.output.emit("脚本执行已终止\n")
        except Exception as e:
            self.output.emit(f"脚本执行错误: {str(e)}\n")
            self.output.emit(traceback.format_exc())


    

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



    def print_colored(self, text, color, background=None, style=None):
        colors = {
            'black': '30',
            'red': '31',
            'green': '32',
            'yellow': '33',
            'blue': '34',
            'purple': '35',
            'cyan': '36',
            'white': '37'
        }
        
        backgrounds = {
            'black': '40',
            'red': '41',
            'green': '42',
            'yellow': '43',
            'blue': '44',
            'purple': '45',
            'cyan': '46',
            'white': '47'
        }
        
        styles = {
            'default': '0',
            'bold': '1',
            'underline': '4',
            'blink': '5',
            'reverse': '7'
        }
        
        color_code = colors.get(color, '37')
        background_code = backgrounds.get(background, '')
        style_code = styles.get(style, '0')
        
        if background_code:
            background_code = ';' + background_code

        formatted_text = f'\033[{style_code};{color_code}{background_code}m{text}\033[0m'
        self.output.emit(formatted_text)



 
