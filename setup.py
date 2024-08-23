from cx_Freeze import setup, Executable
import sys

sys.setrecursionlimit(100000)  # 或者更大的值


# Define your main script
script_name = "main.py"  # 替换为你的脚本名称

#"excludes": ["torch","scipy","sympy"],  # 如果有不需要的模块，可以在这里排除
#"excludes": [],  # 如果有不需要的模块，可以在这里排除
# Define build options
build_options = {
    "packages": ["numpy",'pyvisa','pyvisa_sim'],  # 如果你的代码依赖额外的包，可以在这里列出
    "excludes": ["torch","scipy","sympy"],  # 如果有不需要的模块，可以在这里排除
    #"include_files": ["CH341DLLA64.DLL", "register_map_data.pkl",('./configs/','configs/'),("./logs/","logs/"),("./scripts/","scripts/")],  # 如果有额外的文件或资源，列在这里
    "include_files": ["CH341DLLA64.DLL", "register_map_data.pkl"]  # 如果有额外的文件或资源，列在这里
}
gui_app = True
# Define executables
executables = [
    Executable(
        script_name,
        base="Win32GUI" if sys.platform == "win32" and gui_app else None,  # "Win32GUI" 对于 GUI 应用
        target_name="device_config.exe",  # 设置你希望的可执行文件名
        icon="wework_task_bar_workbench.ico"  # 可选的图标文件
    )
]

# Setup configuration
setup(
    name="device_config",  # 应用程序名称
    version="1.0",  # 应用程序版本
    description="A description of your application",  # 描述
    options={"build_exe": build_options},
    executables=executables
)
