# TwoYaTimer ⏱

一款轻量现代的 **Windows桌面计时器**，深色模式、厘秒精度、计次对比、历史记录一应俱全。

右侧Releases下载即可直接使用

<img width="512" height="739" alt="image" src="https://github.com/user-attachments/assets/f256c302-7e2b-4c3b-88cf-e34e06d90950" />



## 功能特性

- **高精度计时** — 基于 `time.perf_counter()`，60fps 刷新，显示精度到厘秒（0.01s）
- **计次对比** — 每圈自动与最佳圈对比，绿色标注最佳、红色标注最差
- **历史记录** — 自动保存每次完整计时会话（JSON 存储于 `%APPDATA%/TwoYaTimer/`）
- **自适应布局** — 窗口可缩放，计时数字自动适配大小
- **暂停视觉提示** — 暂停时数字闪烁 + 黄色状态指示
- **键盘快捷键** — `Space` 开始/暂停、`L` 计次、`R` 重置、`H` 历史
- **Windows 11 风格** — 深色标题栏、圆角控件、协调配色

## 快速开始

### 运行（开发模式）

```bash
pip install customtkinter
cd src
python main.py
```

### 打包为 EXE

```bash
# 自动安装依赖并打包
build.bat
```

输出：`dist/TwoYaTimer.exe`（双击即可运行，无需安装）

## 项目结构

```
TwoYaTimer/
├── src/
│   ├── main.py              # 入口文件
│   ├── app.py               # 主应用窗口（组装 UI + 事件路由）
│   ├── timer_engine.py      # 计时核心引擎（纯逻辑，无 UI 依赖）
│   ├── widgets/
│   │   ├── timer_display.py  # 自适应计时数字 + 闪烁动画
│   │   ├── control_panel.py  # 开始/暂停/计次/重置按钮组
│   │   ├── lap_list.py       # 可滚动计次列表 + 最佳/最差标注
│   │   └── history_panel.py  # 历史记录弹窗
│   ├── models/
│   │   └── session.py        # 会话/计次数据模型
│   └── utils/
│       ├── constants.py      # 配色、字体、应用常量
│       └── storage.py        # JSON 持久化
├── requirements.txt
├── build.bat                 # 一键打包脚本
└── README.md
```

## 快捷键

| 按键 | 功能 |
|------|------|
| `Space` | 开始 / 暂停 |
| `L` | 计次 |
| `R` | 重置 |
| `H` | 打开历史记录 |
| `Esc` | 关闭历史面板 |

## 技术栈

- **Python 3.10+**
- **CustomTkinter 5.2+** — 现代化 tkinter UI 框架
- **PyInstaller 6.0+** — 打包为单文件 EXE

## 许可证

MIT License
