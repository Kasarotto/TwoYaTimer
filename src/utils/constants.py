"""
TwoYaTimer — 常量定义与配色方案

包含应用全局配置、Windows 11 风格深色配色、字体设定与数据存储配置。
"""

# ═══════════════════════════════════════════
#  应用信息
# ═══════════════════════════════════════════

APP_NAME = "TwoYaTimer"
APP_VERSION = "1.0.0"
WINDOW_MIN_WIDTH = 480
WINDOW_MIN_HEIGHT = 640
WINDOW_DEFAULT_SIZE = "540x740"

# ═══════════════════════════════════════════
#  刷新率配置
# ═══════════════════════════════════════════

# UI 刷新间隔：~60fps，确保厘秒显示流畅且 CPU 开销极低
TIMER_REFRESH_MS = 16


# ═══════════════════════════════════════════
#  深色配色方案 — Windows 11 风格
# ═══════════════════════════════════════════

class Colors:
    """
    所有颜色常量集中管理。
    灰白简约风格。
    """

    # ── 背景层级 ──
    BG_PRIMARY    = "#FAFAFA"   # 主窗口背景（近白）
    BG_SECONDARY  = "#F0F0F0"   # 次级面板
    BG_TERTIARY   = "#E6E6E6"   # 三级元素（行、标签头）
    BG_HOVER      = "#DCDCDC"   # 悬停反馈

    # ── 强调色 ──
    ACCENT_BLUE   = "#4A90D9"   # 主色调
    ACCENT_GREEN  = "#2E8B57"   # 开始 / 正向
    ACCENT_RED    = "#D94A4A"   # 暂停 / 危险
    ACCENT_YELLOW = "#C8960C"   # 暂停状态提示
    ACCENT_PURPLE = "#7B68AE"   # 装饰色（保留）

    # ── 文字 ──
    TEXT_PRIMARY   = "#1A1A1A"  # 主要文字
    TEXT_SECONDARY = "#555555"  # 次要文字
    TEXT_MUTED     = "#999999"  # 弱化文字

    # ── 边框与分割 ──
    BORDER  = "#D0D0D0"
    DIVIDER = "#E0E0E0"

    # ── 按钮专用 ──
    BTN_START_BG       = "#2E8B57"
    BTN_START_HOVER    = "#267348"
    BTN_PAUSE_BG       = "#D94A4A"
    BTN_PAUSE_HOVER    = "#B83A3A"
    BTN_SECONDARY_BG   = "#E0E0E0"
    BTN_SECONDARY_HOVER = "#D0D0D0"

    # ── 计次列表行背景 ──
    LAP_BEST_BG  = "#E8F5E9"
    LAP_WORST_BG = "#FFEBEE"


# ═══════════════════════════════════════════
#  字体配置
# ═══════════════════════════════════════════

class Fonts:
    """
    字体族定义。使用微软雅黑，专为屏幕显示优化。
    TIMER_FAMILY: 计时器主显示数字
    UI_FAMILY:    界面文字（按钮、标签等）
    """
    TIMER_FAMILY   = "微软雅黑"
    TIMER_FALLBACK = "Microsoft YaHei"   # 英文名备选
    UI_FAMILY      = "微软雅黑"


# ═══════════════════════════════════════════
#  数据存储
# ═══════════════════════════════════════════

DATA_FILENAME = "twoya_timer_history.json"
