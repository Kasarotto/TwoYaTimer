"""
TwoYaTimer — 计次列表组件

可滚动的计次记录表格，功能包括：
- 最新一条记录高亮显示
- 新记录插入到顶部（最新在前）
- 显示圈号、累计时间、本圈耗时
"""

import customtkinter as ctk
from utils.constants import Colors, Fonts


class LapList(ctk.CTkFrame):
    """计次记录列表面板。"""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=Colors.BG_SECONDARY,
            corner_radius=12,
            **kwargs,
        )

        self._rows: list = []  # 存储 {"frame": CTkFrame}

        # ── 表头 ──
        header = ctk.CTkFrame(
            self, fg_color=Colors.BG_TERTIARY,
            corner_radius=8, height=40,
        )
        header.pack(fill="x", padx=8, pady=(8, 4))
        header.pack_propagate(False)

        columns = [("#", 60), ("累计时间", 160), ("圈时", 160)]
        for text, width in columns:
            ctk.CTkLabel(
                header, text=text,
                font=(Fonts.UI_FAMILY, 16, "bold"),
                text_color=Colors.TEXT_SECONDARY,
                width=width, anchor="center",
            ).pack(side="left", padx=4)

        # ── 可滚动列表区域 ──
        self._scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Colors.BG_TERTIARY,
            scrollbar_button_hover_color=Colors.BG_HOVER,
        )
        self._scroll_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # ── 空状态提示 ──
        self._empty_label = ctk.CTkLabel(
            self._scroll_frame,
            text="按 L 键或点击「计次」记录圈时",
            font=(Fonts.UI_FAMILY, 16),
            text_color=Colors.TEXT_MUTED,
        )
        self._empty_label.pack(pady=30)

    def add_lap(
        self,
        number: int,
        split_time: float,
        lap_time: float,
    ) -> None:
        """
        添加一条计次记录。

        Args:
            number:     圈号
            split_time: 累计时间
            lap_time:   本圈耗时
        """
        # 隐藏空状态提示
        self._empty_label.pack_forget()

        # ── 取消上一行的高亮 ──
        if self._rows:
            prev = self._rows[-1]
            prev["frame"].configure(fg_color=Colors.BG_SECONDARY)

        # ── 创建行 (插入到列表顶部) ──
        row = ctk.CTkFrame(
            self._scroll_frame,
            fg_color=Colors.BG_TERTIARY,  # 最新行高亮色
            corner_radius=6,
            height=42,
        )
        # 新行插在最前面
        if self._rows:
            row.pack(fill="x", pady=2, before=self._rows[-1]["frame"])
        else:
            row.pack(fill="x", pady=2)
        row.pack_propagate(False)

        # ── 圈号 ──
        ctk.CTkLabel(
            row, text=f"#{number}",
            font=(Fonts.UI_FAMILY, 15, "bold"),
            text_color=Colors.ACCENT_BLUE,
            width=60, anchor="center",
        ).pack(side="left", padx=4)

        # ── 累计时间 ──
        ctk.CTkLabel(
            row, text=self._format_full(split_time),
            font=(Fonts.TIMER_FAMILY, 16),
            text_color=Colors.TEXT_PRIMARY,
            width=160, anchor="center",
        ).pack(side="left", padx=4)

        # ── 圈时 ──
        ctk.CTkLabel(
            row, text=self._format_full(lap_time),
            font=(Fonts.TIMER_FAMILY, 16, "bold"),
            text_color=Colors.TEXT_PRIMARY,
            width=160, anchor="center",
        ).pack(side="left", padx=4)

        self._rows.append({"frame": row})

    def clear(self) -> None:
        """清空所有计次记录。"""
        for row_data in self._rows:
            row_data["frame"].destroy()
        self._rows.clear()
        self._empty_label.pack(pady=30)

    # ── 时间格式化工具 ──

    @staticmethod
    def _format_full(seconds: float) -> str:
        """格式化为 HH:MM:SS.cc 或 MM:SS.cc（小时为 0 时省略）。"""
        total_cs = int(seconds * 100)
        cs = total_cs % 100
        total_s = total_cs // 100
        s = total_s % 60
        total_m = total_s // 60
        m = total_m % 60
        h = total_m // 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}.{cs:02d}"
        return f"{m:02d}:{s:02d}.{cs:02d}"
