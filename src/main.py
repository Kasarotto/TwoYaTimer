"""
TwoYaTimer — 程序入口

启动 CustomTkinter 深色模式应用。
支持 PyInstaller --onefile 打包后的路径处理。
"""

import sys
import os

# ── PyInstaller 打包兼容：确保 src/ 目录在 import 路径中 ──
if getattr(sys, "frozen", False):
    # 打包后：sys.executable 所在目录
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 开发环境：当前脚本所在目录
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 将 src/ 自身加入模块搜索路径（解决 widgets/, models/, utils/ 的导入）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from app import TwoYaTimerApp


def main():
    """配置全局主题并启动主循环。"""
    # 修复高分屏下中文字体模糊问题
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per-Monitor DPI Aware
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()   # 回退方案
        except Exception:
            pass

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = TwoYaTimerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
