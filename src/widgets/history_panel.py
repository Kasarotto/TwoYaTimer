"""
TwoYaTimer — 历史记录面板

以独立弹窗形式展示所有历史计时会话，支持：
- 按时间倒序排列（最新在前）
- 每条记录显示开始时间、总时长、计次摘要
- 单条删除 / 全部清空
- ESC 关闭面板
- Windows 11 深色标题栏
"""

import customtkinter as ctk
from utils.constants import Colors, Fonts
from utils.storage import Storage
from models.session import TimerSession


class HistoryPanel(ctk.CTkToplevel):
    """历史记录弹窗。"""

    def __init__(self, master, storage: Storage, **kwargs):
        super().__init__(master, **kwargs)

        self.title("计时历史记录")
        self.geometry("520x620")
        self.configure(fg_color=Colors.BG_PRIMARY)
        self.minsize(400, 300)

        self._storage = storage

        # ── 标题栏 ──
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(
            title_frame,
            text="📋  计时历史记录",
            font=(Fonts.UI_FAMILY, 20, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(side="left")

        ctk.CTkButton(
            title_frame,
            text="清空全部",
            width=80, height=32,
            font=(Fonts.UI_FAMILY, 15),
            fg_color=Colors.BTN_PAUSE_BG,
            hover_color=Colors.BTN_PAUSE_HOVER,
            corner_radius=8,
            command=self._clear_all,
        ).pack(side="right")

        # ── 可滚动列表 ──
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Colors.BG_TERTIARY,
            scrollbar_button_hover_color=Colors.BG_HOVER,
        )
        self._scroll.pack(fill="both", expand=True, padx=16, pady=8)

        self._load_history()

        # ESC 关闭
        self.bind("<Escape>", lambda _: self.destroy())
        self.focus_force()


    def _load_history(self) -> None:
        """加载并渲染历史列表。"""
        # 清除现有内容
        for widget in self._scroll.winfo_children():
            widget.destroy()

        sessions = self._storage.load_sessions()

        if not sessions:
            ctk.CTkLabel(
                self._scroll,
                text="暂无历史记录\n\n完成一次计时后自动保存",
                font=(Fonts.UI_FAMILY, 14),
                text_color=Colors.TEXT_MUTED,
                justify="center",
            ).pack(pady=60)
            return

        for session in sessions:
            self._create_session_card(session)

    def _create_session_card(self, session: TimerSession) -> None:
        """为单个会话创建卡片视图。"""
        card = ctk.CTkFrame(
            self._scroll,
            fg_color=Colors.BG_SECONDARY,
            corner_radius=10,
        )
        card.pack(fill="x", pady=4)

        # ── 第一行：日期 + 删除按钮 ──
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(10, 4))

        # 格式化日期显示
        date_display = self._format_datetime(session.start_datetime)
        ctk.CTkLabel(
            top_row,
            text=f"🕐  {date_display}",
            font=(Fonts.UI_FAMILY, 15),
            text_color=Colors.TEXT_SECONDARY,
        ).pack(side="left")

        ctk.CTkButton(
            top_row,
            text="✕", width=28, height=28,
            font=(Fonts.UI_FAMILY, 14),
            fg_color="transparent",
            hover_color=Colors.BTN_PAUSE_BG,
            text_color=Colors.TEXT_MUTED,
            corner_radius=6,
            command=lambda sid=session.id: self._delete_session(sid),
        ).pack(side="right")

        # ── 总时长（大字醒目）──
        ctk.CTkLabel(
            card,
            text=self._format_duration(session.total_duration),
            font=(Fonts.TIMER_FALLBACK, 24, "bold"),
            text_color=Colors.ACCENT_BLUE,
        ).pack(padx=12, anchor="w")

        # ── 计次摘要 ──
        if session.laps:
            lap_count = len(session.laps)
            best = min(lap.lap_time for lap in session.laps)
            summary = f"{lap_count} 个计次  ·  最佳圈 {self._format_duration(best)}"
        else:
            summary = "无计次记录"

        ctk.CTkLabel(
            card, text=summary,
            font=(Fonts.UI_FAMILY, 15),
            text_color=Colors.TEXT_MUTED,
        ).pack(padx=12, pady=(0, 10), anchor="w")

    def _delete_session(self, session_id: str) -> None:
        """删除单条历史记录并刷新列表。"""
        self._storage.delete_session(session_id)
        self._load_history()

    def _clear_all(self) -> None:
        """清空所有历史记录。"""
        self._storage.save_sessions([])
        self._load_history()

    # ── 格式化工具 ──

    @staticmethod
    def _format_datetime(iso_str: str) -> str:
        """将 ISO 时间戳格式化为友好显示。"""
        if not iso_str:
            return "未知时间"
        try:
            # "2026-09-29T14:30:00.123456" → "2026-09-29  14:30:00"
            return iso_str[:19].replace("T", "  ")
        except (IndexError, ValueError):
            return iso_str

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """格式化时长为 HH:MM:SS.cc。"""
        total_cs = int(seconds * 100)
        cs = total_cs % 100
        total_s = total_cs // 100
        s = total_s % 60
        total_m = total_s // 60
        m = total_m % 60
        h = total_m // 60
        return f"{h:02d}:{m:02d}:{s:02d}.{cs:02d}"
