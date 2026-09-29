"""
TwoYaTimer — 系统托盘支持 (Windows Native ctypes)

无需任何第三方库 (如 pystray / PIL / win32gui)，
使用 Windows 内置 Shell_NotifyIconW 和 TrackPopupMenu 实现原生系统托盘：
- 单击/双击托盘图标：显示/隐藏窗口
- 右键托盘图标：弹出菜单【显示/隐藏】、【退出软件】
- 零第三方依赖，保持单文件打包体积低于 10MB
"""

import ctypes
from ctypes import wintypes
import threading
from typing import Callable, Optional

user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32
kernel32 = ctypes.windll.kernel32

# ══════ 常量定义 ══════
WM_DESTROY = 0x0002
WM_USER = 0x0400
WM_TRAY = WM_USER + 20

WM_LBUTTONUP = 0x0202
WM_LBUTTONDBLCLK = 0x0203
WM_RBUTTONUP = 0x0205

NIM_ADD = 0x00000000
NIM_MODIFY = 0x00000001
NIM_DELETE = 0x00000002

NIF_MESSAGE = 0x00000001
NIF_ICON = 0x00000002
NIF_TIP = 0x00000004

TPM_LEFTALIGN = 0x0000
TPM_RIGHTBUTTON = 0x0002
TPM_RETURNCMD = 0x0100

MF_STRING = 0x00000000
MF_SEPARATOR = 0x00000800

IDI_APPLICATION = 32512

CMD_TOGGLE = 1001
CMD_EXIT = 1002

# ══════ Python 3.8+ 句柄兼容性定义 ══════
HANDLE = wintypes.HANDLE
HWND = getattr(wintypes, "HWND", HANDLE)
HINSTANCE = getattr(wintypes, "HINSTANCE", HANDLE)
HICON = getattr(wintypes, "HICON", HANDLE)
HCURSOR = getattr(wintypes, "HCURSOR", HANDLE)
HBRUSH = getattr(wintypes, "HBRUSH", HANDLE)
HMENU = getattr(wintypes, "HMENU", HANDLE)
LPCWSTR = getattr(wintypes, "LPCWSTR", ctypes.c_wchar_p)
UINT = getattr(wintypes, "UINT", ctypes.c_uint)
DWORD = getattr(wintypes, "DWORD", ctypes.c_ulong)
WPARAM = getattr(wintypes, "WPARAM", ctypes.c_size_t)
LPARAM = getattr(wintypes, "LPARAM", ctypes.c_ssize_t)

# ══════ Windows 结构体 ══════
WNDPROC = ctypes.WINFUNCTYPE(
    ctypes.c_longlong,
    HWND,
    UINT,
    WPARAM,
    LPARAM,
)


class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", UINT),
        ("style", UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", HINSTANCE),
        ("hIcon", HICON),
        ("hCursor", HCURSOR),
        ("hbrBackground", HBRUSH),
        ("lpszMenuName", LPCWSTR),
        ("lpszClassName", LPCWSTR),
        ("hIconSm", HICON),
    ]


class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ("cbSize", DWORD),
        ("hWnd", HWND),
        ("uID", UINT),
        ("uFlags", UINT),
        ("uCallbackMessage", UINT),
        ("hIcon", HICON),
        ("szTip", wintypes.WCHAR * 128),
        ("dwState", DWORD),
        ("dwStateMask", DWORD),
        ("szInfo", wintypes.WCHAR * 256),
        ("uTimeoutOrVersion", UINT),
        ("szInfoTitle", wintypes.WCHAR * 64),
        ("dwInfoFlags", DWORD),
        ("guidItem", ctypes.c_byte * 16),
        ("hBalloonIcon", HICON),
    ]


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


# 函数签名
user32.DefWindowProcW.argtypes = [HWND, UINT, WPARAM, LPARAM]
user32.DefWindowProcW.restype = ctypes.c_longlong

user32.CreateWindowExW.argtypes = [
    DWORD, LPCWSTR, LPCWSTR, DWORD,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    HWND, HMENU, HINSTANCE, ctypes.c_void_p,
]
user32.CreateWindowExW.restype = HWND

user32.LoadIconW.argtypes = [HINSTANCE, ctypes.c_void_p]
user32.LoadIconW.restype = HICON



class SystemTray:
    """
    原生 Windows 系统托盘控制器。
    在独立后台线程中运行隐藏消息窗口和消息循环。
    """

    def __init__(
        self,
        tooltip: str = "TwoYaTimer",
        on_toggle: Optional[Callable[[], None]] = None,
        on_quit: Optional[Callable[[], None]] = None,
    ):
        self.tooltip = tooltip
        self.on_toggle = on_toggle
        self.on_quit = on_quit

        self._hwnd: Optional[int] = None
        self._thread: Optional[threading.Thread] = None
        self._ready_event = threading.Event()
        self._alive = False

        # 必须作为成员变量持有，防止 Python 垃圾回收导致回调崩溃
        self._wnd_proc = WNDPROC(self._window_proc)

    def start(self) -> None:
        """启动托盘图标线程。"""
        if self._alive:
            return
        self._alive = True
        self._ready_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        # 等待后台窗口创建并添加托盘图标完毕
        self._ready_event.wait(timeout=2.0)

    def stop(self) -> None:
        """移除托盘图标并退出后台线程。"""
        if not self._alive:
            return
        self._alive = False

        if self._hwnd:
            # 从托盘移除图标
            nid = NOTIFYICONDATAW()
            nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
            nid.hWnd = self._hwnd
            nid.uID = 1
            shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(nid))

            # 销毁窗口
            user32.PostMessageW(self._hwnd, WM_DESTROY, 0, 0)
            self._hwnd = None

    def _run(self) -> None:
        """后台线程：注册窗口类、创建隐藏窗口、添加托盘、运行消息泵。"""
        class_name = f"TwoYaTimerTray_{id(self)}"
        hinst = kernel32.GetModuleHandleW(None)

        # 1. 尝试获取程序图标
        hicon = user32.LoadIconW(hinst, ctypes.c_void_p(1))
        if not hicon:
            hicon = user32.LoadIconW(None, ctypes.c_void_p(IDI_APPLICATION))

        # 2. 注册窗口类
        wc = WNDCLASSEXW()
        wc.cbSize = ctypes.sizeof(WNDCLASSEXW)
        wc.style = 0
        wc.lpfnWndProc = self._wnd_proc
        wc.cbClsExtra = 0
        wc.cbWndExtra = 0
        wc.hInstance = hinst
        wc.hIcon = hicon
        wc.hCursor = 0
        wc.hbrBackground = 0
        wc.lpszMenuName = None
        wc.lpszClassName = class_name
        wc.hIconSm = hicon

        atom = user32.RegisterClassExW(ctypes.byref(wc))
        if not atom:
            self._ready_event.set()
            return

        # 3. 创建隐藏消息窗口
        self._hwnd = user32.CreateWindowExW(
            0,
            class_name,
            "TwoYaTimerTrayMsgWindow",
            0,
            0, 0, 0, 0,
            None, None,
            hinst,
            None,
        )

        if not self._hwnd:
            self._ready_event.set()
            return

        # 4. 添加托盘图标
        nid = NOTIFYICONDATAW()
        nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
        nid.hWnd = self._hwnd
        nid.uID = 1
        nid.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
        nid.uCallbackMessage = WM_TRAY
        nid.hIcon = hicon
        nid.szTip = self.tooltip[:127]

        shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid))
        self._ready_event.set()

        # 5. 消息循环
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        user32.UnregisterClassW(class_name, hinst)

    def _window_proc(self, hwnd: int, msg: int, wparam: int, lparam: int) -> int:
        """窗口过程：处理托盘通知和菜单选择。"""
        if msg == WM_TRAY:
            # 鼠标左键点击或双击：切换显示/隐藏
            if lparam in (WM_LBUTTONUP, WM_LBUTTONDBLCLK):
                if self.on_toggle:
                    self.on_toggle()
                return 0

            # 鼠标右键：弹出上下文菜单
            elif lparam == WM_RBUTTONUP:
                self._show_context_menu(hwnd)
                return 0

        elif msg == WM_DESTROY:
            user32.PostQuitMessage(0)
            return 0

        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    def _show_context_menu(self, hwnd: int) -> None:
        """显示托盘右键菜单。"""
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))

        # Windows 要求在 TrackPopupMenu 之前调用 SetForegroundWindow
        user32.SetForegroundWindow(hwnd)

        hmenu = user32.CreatePopupMenu()
        user32.AppendMenuW(hmenu, MF_STRING, CMD_TOGGLE, "显示/隐藏")
        user32.AppendMenuW(hmenu, MF_SEPARATOR, 0, None)
        user32.AppendMenuW(hmenu, MF_STRING, CMD_EXIT, "退出软件")

        # 同步返回选择的菜单项 ID
        cmd = user32.TrackPopupMenu(
            hmenu,
            TPM_RIGHTBUTTON | TPM_RETURNCMD,
            pt.x,
            pt.y,
            0,
            hwnd,
            None,
        )

        user32.PostMessageW(hwnd, 0, 0, 0)
        user32.DestroyMenu(hmenu)

        if cmd == CMD_TOGGLE:
            if self.on_toggle:
                self.on_toggle()
        elif cmd == CMD_EXIT:
            if self.on_quit:
                self.on_quit()
