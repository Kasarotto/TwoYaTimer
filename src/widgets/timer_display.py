"""
TwoYaTimer — 计时数字显示组件

大字号居中显示当前计时，支持：
- 窗口缩放时字体自适应
- 暂停状态闪烁动画
- 运行/暂停/停止三种视觉状态
"""

import customtkinter as ctk
import tkinter.font as tkfont
from utils.constants import Colors, Fonts


class TimerDisplay(ctk.CTkFrame):
    """
    计时器主显示区域。

    自动根据父容器宽度调整字体大小，
    暂停时数字以 500ms 间隔闪烁明暗提示用户。
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._time_text: str = "00:00:00.00"
        self._font_size: int = 72
        self._is_paused: bool = False

        # ── 检测可用字体 ──
        self._timer_font = self._pick_font()

        # ── 时间标签（核心元素）──
        self._label = ctk.CTkLabel(
            self,
            text=self._time_text,
            font=(self._timer_font, self._font_size, "bold"),
            text_color=Colors.TEXT_SECONDARY,  # 初始状态为浅灰（停止态）
        )
        self._label.pack(expand=True, fill="both")

        # ── 状态指示文字 ──
        self._status_label = ctk.CTkLabel(
            self,
            text="",
            font=(Fonts.UI_FAMILY, 15),
            text_color=Colors.TEXT_SECONDARY,
            height=22,
        )
        self._status_label.pack(pady=(0, 4))

        # ── 窗口缩放监听 ──
        self.bind("<Configure>", self._on_resize)

        # ── 闪烁动画控制 ──
        self._blink_visible: bool = True
        self._blink_job = None

    def _pick_font(self) -> str:
        """选择系统中可用的等宽字体，优先 Cascadia Mono。"""
        available = tkfont.families()
        if Fonts.TIMER_FAMILY in available:
            return Fonts.TIMER_FAMILY
        if Fonts.TIMER_FALLBACK in available:
            return Fonts.TIMER_FALLBACK
        return "Courier"  # 终极回退

    def _on_resize(self, event):
        """根据容器宽度自适应字体大小，10 个字符约占满 80% 宽度。"""
        width = event.width
        # 经验公式：宽度 / 7.5，限制在 [28, 130] 范围内
        new_size = max(28, min(130, int(width / 7.5)))
        if abs(new_size - self._font_size) >= 2:  # 避免频繁重绘
            self._font_size = new_size
            self._label.configure(
                font=(self._timer_font, self._font_size, "bold")
            )

    # ── 时间更新 ──

    def update_time(self, time_str: str) -> None:
        """刷新显示的时间字符串。"""
        self._time_text = time_str
        # 闪烁暗态时不更新文本（保持视觉一致性）
        if self._blink_visible or not self._is_paused:
            self._label.configure(text=time_str)

    # ── 状态切换 ──

    def set_running(self) -> None:
        """切换到运行态：白色文字 + 绿色状态指示。"""
        self._is_paused = False
        self._stop_blink()
        self._label.configure(text_color=Colors.TEXT_PRIMARY)
        self._status_label.configure(
            text="● 计时中", text_color=Colors.ACCENT_GREEN
        )

    def set_paused(self, paused: bool) -> None:
        """切换到暂停态：启动闪烁 + 黄色状态指示。"""
        self._is_paused = paused
        if paused:
            self._status_label.configure(
                text="⏸ 已暂停", text_color=Colors.ACCENT_YELLOW
            )
            self._start_blink()
        else:
            self._stop_blink()
            self._label.configure(text_color=Colors.TEXT_PRIMARY)
            self._status_label.configure(text="")

    def set_stopped(self) -> None:
        """切换到停止态：浅灰文字，无状态指示。"""
        self._is_paused = False
        self._stop_blink()
        self._label.configure(text_color=Colors.TEXT_SECONDARY)
        self._status_label.configure(text="")

    # ── 闪烁动画 ──

    def _start_blink(self) -> None:
        """启动暂停闪烁效果。"""
        self._stop_blink()
        self._blink_visible = True
        self._do_blink()

    def _do_blink(self) -> None:
        """交替切换文字明暗，500ms 一帧。"""
        self._blink_visible = not self._blink_visible
        color = Colors.TEXT_PRIMARY if self._blink_visible else Colors.TEXT_MUTED
        self._label.configure(text_color=color)
        self._blink_job = self.after(500, self._do_blink)

    def _stop_blink(self) -> None:
        """停止闪烁并恢复正常颜色。"""
        if self._blink_job is not None:
            self.after_cancel(self._blink_job)
            self._blink_job = None
        self._blink_visible = True
        self._label.configure(text_color=Colors.TEXT_PRIMARY)
