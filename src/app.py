"""
TwoYaTimer — 主应用窗口

组装所有 UI 组件，协调计时引擎与界面的交互：
- 计时显示、控制按钮、计次列表、历史面板
- 键盘快捷键绑定
- 会话自动保存（重置/关闭时触发）
- Windows 11 深色标题栏
"""

import customtkinter as ctk
from datetime import datetime

from timer_engine import TimerEngine, TimerState
from widgets.timer_display import TimerDisplay
from widgets.control_panel import ControlPanel
from widgets.lap_list import LapList
from widgets.history_panel import HistoryPanel
from models.session import TimerSession, LapRecord
from utils.storage import Storage
from utils.tray import SystemTray
from utils.constants import (
    Colors, Fonts, APP_NAME, APP_VERSION,
    WINDOW_DEFAULT_SIZE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    TIMER_REFRESH_MS,
)


class TwoYaTimerApp(ctk.CTk):
    """
    TwoYaTimer 主窗口。

    职责：
    1. 搭建 UI 布局
    2. 将按钮/快捷键事件路由到 TimerEngine
    3. 驱动 60fps 刷新循环
    4. 管理会话生命周期（自动保存到 Storage）
    """

    def __init__(self):
        super().__init__()

        # ══════ 窗口基础配置 ══════
        self.title(APP_NAME)
        self.geometry(WINDOW_DEFAULT_SIZE)
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.configure(fg_color=Colors.BG_PRIMARY)

        # ══════ 核心组件 ══════
        self._engine = TimerEngine()
        self._storage = Storage()
        self._session_start_dt: str | None = None   # 当前会话开始时间
        self._history_window = None                  # 历史面板引用（单例）
        self._update_job = None                      # after() 回调 ID

        # ══════ 构建界面 ══════
        self._build_ui()

        # ══════ 键盘快捷键 ══════
        self.bind("<space>", self._on_space)
        self.bind("<KeyPress-l>", lambda _: self._on_lap())
        self.bind("<KeyPress-L>", lambda _: self._on_lap())
        self.bind("<KeyPress-r>", lambda _: self._on_reset())
        self.bind("<KeyPress-R>", lambda _: self._on_reset())
        self.bind("<KeyPress-h>", lambda _: self._show_history())
        self.bind("<KeyPress-H>", lambda _: self._show_history())

        # ══════ 系统托盘（点击关闭最小化到托盘） ══════
        self._tray = SystemTray(
            tooltip=APP_NAME,
            on_toggle=lambda: self.after(0, self._toggle_window),
            on_quit=lambda: self.after(0, self._exit_app),
        )
        self._tray.start()

        # ══════ 窗口关闭处理（隐藏到托盘） ══════
        self.protocol("WM_DELETE_WINDOW", self._on_close_clicked)

    # ─────────────────────────────────────
    #  UI 构建
    # ─────────────────────────────────────

    def _build_ui(self) -> None:
        """搭建完整的界面布局。"""

        # ── 顶部标题栏 ──
        header = ctk.CTkFrame(self, fg_color="transparent", height=40)
        header.pack(fill="x", padx=20, pady=(12, 0))
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text=APP_NAME,
            font=(Fonts.UI_FAMILY, 16, "bold"),
            text_color=Colors.ACCENT_BLUE,
        ).pack(side="left")

        # 历史按钮（右上角）
        self._history_btn = ctk.CTkButton(
            header,
            text="📋 历史",
            font=(Fonts.UI_FAMILY, 15),
            width=80, height=32,
            corner_radius=8,
            fg_color=Colors.BTN_SECONDARY_BG,
            hover_color=Colors.BTN_SECONDARY_HOVER,
            text_color=Colors.TEXT_SECONDARY,
            command=self._show_history,
        )
        self._history_btn.pack(side="right")

        # 快捷键提示
        # ctk.CTkLabel(
        #     header,
        #     text="Space·开始/暂停  L·计次  R·重置  H·历史",
        #     font=(Fonts.UI_FAMILY, 13),
        #     text_color=Colors.TEXT_MUTED,
        # ).pack(side="right", padx=10)

        # ── 计时数字显示区 ──
        self._timer_display = TimerDisplay(self)
        self._timer_display.pack(fill="x", padx=20, pady=(20, 10), ipady=30)

        # ── 控制按钮区 ──
        self._control_panel = ControlPanel(
            self,
            on_start=self._on_start,
            on_pause=self._on_pause,
            on_lap=self._on_lap,
            on_reset=self._on_reset,
        )
        self._control_panel.pack(fill="x", padx=20, pady=8)

        # ── 分割线 ──
        ctk.CTkFrame(
            self, fg_color=Colors.DIVIDER, height=1,
        ).pack(fill="x", padx=30, pady=8)

        # ── 计次列表区（占据剩余空间） ──
        self._lap_list = LapList(self)
        self._lap_list.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    # ─────────────────────────────────────
    #  计时控制回调
    # ─────────────────────────────────────

    def _on_start(self) -> None:
        """开始或恢复计时。"""
        if self._engine.state == TimerState.STOPPED:
            self._session_start_dt = datetime.now().isoformat()
        self._engine.start()
        self._timer_display.set_running()
        self._control_panel.set_running()
        self._start_update_loop()

    def _on_pause(self) -> None:
        """暂停计时。"""
        self._engine.pause()
        self._timer_display.set_paused(True)
        self._timer_display.update_time(self._format_elapsed())
        self._control_panel.set_paused()
        self._stop_update_loop()

    def _on_lap(self) -> None:
        """记录一次计次。"""
        result = self._engine.lap()
        if result is None:
            return

        number, split_time, lap_time = result
        self._lap_list.add_lap(number, split_time, lap_time)

    def _on_reset(self) -> None:
        """重置计时器（先保存当前会话）。"""
        # 至少计时 0.5 秒才保存，避免误触产生垃圾记录
        if self._engine.elapsed() > 0.5:
            self._save_current_session()

        self._engine.reset()
        self._timer_display.update_time("00:00:00.00")
        self._timer_display.set_stopped()
        self._control_panel.set_stopped()
        self._lap_list.clear()
        self._stop_update_loop()
        self._session_start_dt = None

    def _on_space(self, event) -> str:
        """空格键：切换开始/暂停。返回 'break' 阻止事件冒泡到按钮。"""
        if self._engine.state == TimerState.RUNNING:
            self._on_pause()
        else:
            self._on_start()
        return "break"

    # ─────────────────────────────────────
    #  60fps 刷新循环
    # ─────────────────────────────────────

    def _start_update_loop(self) -> None:
        """启动 UI 刷新定时器。"""
        self._stop_update_loop()
        self._update_tick()

    def _update_tick(self) -> None:
        """单帧刷新：更新计时显示，然后预约下一帧。"""
        if self._engine.state == TimerState.RUNNING:
            self._timer_display.update_time(self._format_elapsed())
            self._update_job = self.after(TIMER_REFRESH_MS, self._update_tick)

    def _stop_update_loop(self) -> None:
        """停止 UI 刷新定时器。"""
        if self._update_job is not None:
            self.after_cancel(self._update_job)
            self._update_job = None

    # ─────────────────────────────────────
    #  时间格式化
    # ─────────────────────────────────────

    def _format_elapsed(self) -> str:
        """将引擎耗时格式化为 HH:MM:SS.cc 显示字符串。"""
        total = self._engine.elapsed()
        total_cs = int(total * 100)
        cs = total_cs % 100
        total_s = total_cs // 100
        s = total_s % 60
        total_m = total_s // 60
        m = total_m % 60
        h = total_m // 60
        return f"{h:02d}:{m:02d}:{s:02d}.{cs:02d}"

    # ─────────────────────────────────────
    #  会话持久化
    # ─────────────────────────────────────

    def _save_current_session(self) -> None:
        """将当前计时会话保存到历史记录。"""
        session = TimerSession(
            start_datetime=self._session_start_dt or datetime.now().isoformat(),
            end_datetime=datetime.now().isoformat(),
            total_duration=self._engine.elapsed(),
            laps=[
                LapRecord(number=i + 1, split_time=split, lap_time=lap)
                for i, (split, lap) in enumerate(self._engine.laps)
            ],
        )
        self._storage.add_session(session)

    # ─────────────────────────────────────
    #  历史面板
    # ─────────────────────────────────────

    def _show_history(self) -> None:
        """打开/聚焦历史记录面板（单例模式）。"""
        if self._history_window is not None:
            try:
                if self._history_window.winfo_exists():
                    self._history_window.focus_force()
                    return
            except Exception:
                pass
        self._history_window = HistoryPanel(self, self._storage)

    # ─────────────────────────────────────
    #  窗口与系统托盘管理
    # ─────────────────────────────────────

    def _on_close_clicked(self) -> None:
        """点击右上角关闭按钮：不真正关闭，而是最小化隐藏到系统托盘。"""
        self.withdraw()
        if self._history_window is not None:
            try:
                if self._history_window.winfo_exists():
                    self._history_window.withdraw()
            except Exception:
                pass

    def _toggle_window(self) -> None:
        """托盘菜单【显示/隐藏】或点击托盘图标：切换主窗口显示与隐藏。"""
        # 如果窗口当前隐藏或最小化，则显示并置顶激活
        if self.state() == "withdrawn" or not self.winfo_viewable():
            self.deiconify()
            self.state("normal")
            self.lift()
            self.focus_force()
        else:
            self._on_close_clicked()

    def _exit_app(self) -> None:
        """托盘菜单【退出软件】：真正退出软件。"""
        # 1. 移除托盘图标
        if hasattr(self, "_tray") and self._tray:
            self._tray.stop()
        # 2. 保存未完成的会话
        if self._engine.elapsed() > 0.5:
            self._save_current_session()
        # 3. 停止刷新循环并销毁窗口
        self._stop_update_loop()
        super().destroy()

    def destroy(self) -> None:
        """兜底清理：确保托盘图标被移除。"""
        if hasattr(self, "_tray") and self._tray:
            self._tray.stop()
        super().destroy()

