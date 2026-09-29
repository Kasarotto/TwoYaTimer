"""
TwoYaTimer — 按钮控制面板

提供开始/暂停、计次、重置三个主操作按钮。
按钮状态随计时器状态自动切换外观和可用性。
"""

import customtkinter as ctk
from utils.constants import Colors, Fonts


class ControlPanel(ctk.CTkFrame):
    """
    计时器操作按钮组。

    布局：[开始/暂停]  [计次]  [重置]
    - 主按钮（开始/暂停）根据状态切换颜色和文字
    - 次级按钮在不可用时变灰
    """

    def __init__(self, master, *, on_start, on_pause, on_lap, on_reset, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._on_start = on_start
        self._on_pause = on_pause
        self._on_lap = on_lap
        self._on_reset = on_reset
        self._is_running: bool = False

        # ── 按钮容器（居中） ──
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=8)

        # ── 开始/暂停（主按钮） ──
        self._start_pause_btn = ctk.CTkButton(
            btn_frame,
            text="▶  开始",
            font=(Fonts.UI_FAMILY, 16, "bold"),
            width=150, height=50,
            corner_radius=12,
            fg_color=Colors.BTN_START_BG,
            hover_color=Colors.BTN_START_HOVER,
            command=self._toggle_start_pause,
        )
        self._start_pause_btn.pack(side="left", padx=6)

        # ── 计次按钮 ──
        self._lap_btn = ctk.CTkButton(
            btn_frame,
            text="⏱  计次",
            font=(Fonts.UI_FAMILY, 16),
            width=110, height=50,
            corner_radius=12,
            fg_color=Colors.BTN_SECONDARY_BG,
            hover_color=Colors.BTN_SECONDARY_HOVER,
            text_color=Colors.TEXT_MUTED,
            command=self._on_lap,
            state="disabled",
        )
        self._lap_btn.pack(side="left", padx=6)

        # ── 重置按钮 ──
        self._reset_btn = ctk.CTkButton(
            btn_frame,
            text="↺  重置",
            font=(Fonts.UI_FAMILY, 16),
            width=110, height=50,
            corner_radius=12,
            fg_color=Colors.BTN_SECONDARY_BG,
            hover_color=Colors.BTN_SECONDARY_HOVER,
            text_color=Colors.TEXT_MUTED,
            command=self._on_reset,
            state="disabled",
        )
        self._reset_btn.pack(side="left", padx=6)

    def _toggle_start_pause(self) -> None:
        """根据当前状态切换开始/暂停。"""
        if self._is_running:
            self._on_pause()
        else:
            self._on_start()

    # ── 状态切换 ──

    def set_running(self) -> None:
        """运行态：主按钮变红色「暂停」，计次可用，重置禁用。"""
        self._is_running = True
        self._start_pause_btn.configure(
            text="⏸  暂停",
            fg_color=Colors.BTN_PAUSE_BG,
            hover_color=Colors.BTN_PAUSE_HOVER,
        )
        self._lap_btn.configure(
            state="normal", text_color=Colors.TEXT_PRIMARY
        )
        self._reset_btn.configure(
            state="disabled", text_color=Colors.TEXT_MUTED
        )

    def set_paused(self) -> None:
        """暂停态：主按钮变绿色「继续」，计次禁用，重置可用。"""
        self._is_running = False
        self._start_pause_btn.configure(
            text="▶  继续",
            fg_color=Colors.BTN_START_BG,
            hover_color=Colors.BTN_START_HOVER,
        )
        self._lap_btn.configure(
            state="disabled", text_color=Colors.TEXT_MUTED
        )
        self._reset_btn.configure(
            state="normal", text_color=Colors.TEXT_PRIMARY
        )

    def set_stopped(self) -> None:
        """停止态：主按钮变绿色「开始」，计次和重置均禁用。"""
        self._is_running = False
        self._start_pause_btn.configure(
            text="▶  开始",
            fg_color=Colors.BTN_START_BG,
            hover_color=Colors.BTN_START_HOVER,
        )
        self._lap_btn.configure(
            state="disabled", text_color=Colors.TEXT_MUTED
        )
        self._reset_btn.configure(
            state="disabled", text_color=Colors.TEXT_MUTED
        )
