import sys
from cx_Freeze import setup, Executable

# Включите ваши модули в список, если они необходимы
build_exe_options = {
    "packages": ["requests", "PyQt6"],
    "excludes": [],
    "include_files": []
}

# Указание параметров сборки
setup(
    name = "TeachBot",
    version = "1.0.0-alpha",
    description = "Alpha version of app",
    options = {"build_exe": build_exe_options},
    executables = [Executable("main.py", base=None)]
)
