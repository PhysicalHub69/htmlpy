import ctypes
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

LRESULT = ctypes.c_ssize_t

# ============================================================
# Win32 constants
# ============================================================

CS_HREDRAW = 0x0002
CS_VREDRAW = 0x0001

WS_OVERLAPPEDWINDOW = 0x00CF0000

CW_USEDEFAULT = 0x80000000
SW_SHOW = 5

WM_DESTROY = 0x0002
WM_CLOSE = 0x0010
WM_PAINT = 0x000F
WM_SIZE = 0x0005

IDC_ARROW = 32512


# ============================================================
# Win32 structures
# ============================================================

WNDPROC = ctypes.WINFUNCTYPE(
    LRESULT,
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
)


class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HANDLE),
        ("hbrBackground", wintypes.HANDLE),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]


class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [
        ("hdc", wintypes.HDC),
        ("fErase", wintypes.BOOL),
        ("rcPaint", wintypes.RECT),
        ("fRestore", wintypes.BOOL),
        ("fIncUpdate", wintypes.BOOL),
        ("rgbReserved", wintypes.BYTE * 32),
    ]


# ============================================================
# Win32 function signatures
# ============================================================

user32.DefWindowProcW.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
]
user32.DefWindowProcW.restype = LRESULT

user32.RegisterClassW.argtypes = [
    ctypes.POINTER(WNDCLASSW)
]
user32.RegisterClassW.restype = wintypes.ATOM

user32.CreateWindowExW.argtypes = [
    wintypes.DWORD,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.HWND,
    wintypes.HMENU,
    wintypes.HINSTANCE,
    wintypes.LPVOID,
]
user32.CreateWindowExW.restype = wintypes.HWND

user32.ShowWindow.argtypes = [
    wintypes.HWND,
    ctypes.c_int,
]

user32.UpdateWindow.argtypes = [
    wintypes.HWND,
]

user32.DestroyWindow.argtypes = [
    wintypes.HWND,
]

user32.PostQuitMessage.argtypes = [
    ctypes.c_int,
]

user32.TranslateMessage.argtypes = [
    ctypes.POINTER(wintypes.MSG),
]

user32.DispatchMessageW.argtypes = [
    ctypes.POINTER(wintypes.MSG),
]

user32.GetMessageW.argtypes = [
    ctypes.POINTER(wintypes.MSG),
    wintypes.HWND,
    wintypes.UINT,
    wintypes.UINT,
]
user32.GetMessageW.restype = ctypes.c_int

user32.LoadCursorW.argtypes = [
    wintypes.HINSTANCE,
    wintypes.LPCWSTR,
]
user32.LoadCursorW.restype = wintypes.HANDLE

user32.BeginPaint.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(PAINTSTRUCT),
]
user32.BeginPaint.restype = wintypes.HDC

user32.EndPaint.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(PAINTSTRUCT),
]

user32.InvalidateRect.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(wintypes.RECT),
    wintypes.BOOL,
]

kernel32.GetModuleHandleW.argtypes = [
    wintypes.LPCWSTR,
]
kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE


# ============================================================
# Canvas
# ============================================================

class Canvas:

    _class_registered = False

    def __init__(
        self,
        title="Canvas",
        width=800,
        height=600,
    ):
        self.title = title
        self.width = width
        self.height = height

        self.running = False
        self.closed = False

        self.hinstance = kernel32.GetModuleHandleW(None)

        self.class_name = "HTMLPyCanvasWindow"

        # ----------------------------------------------------
        # Window procedure
        # ----------------------------------------------------

        @WNDPROC
        def wnd_proc(hwnd, message, wparam, lparam):

            if message == WM_CLOSE:
                user32.DestroyWindow(hwnd)
                return 0

            if message == WM_DESTROY:
                self.running = False
                self.closed = True
                user32.PostQuitMessage(0)
                return 0

            if message == WM_SIZE:
                self.width = lparam & 0xFFFF
                self.height = (lparam >> 16) & 0xFFFF

                self.on_resize(
                    self.width,
                    self.height
                )

                return 0

            if message == WM_PAINT:

                paint = PAINTSTRUCT()

                hdc = user32.BeginPaint(
                    hwnd,
                    ctypes.byref(paint)
                )

                self.on_draw(hdc)

                user32.EndPaint(
                    hwnd,
                    ctypes.byref(paint)
                )

                return 0

            return user32.DefWindowProcW(
                hwnd,
                message,
                wparam,
                lparam,
            )

        self._wnd_proc = wnd_proc

        # ----------------------------------------------------
        # Register class
        # ----------------------------------------------------

        if not Canvas._class_registered:

            wc = WNDCLASSW()

            wc.style = CS_HREDRAW | CS_VREDRAW
            wc.lpfnWndProc = self._wnd_proc
            wc.cbClsExtra = 0
            wc.cbWndExtra = 0
            wc.hInstance = self.hinstance
            wc.hIcon = None

            wc.hCursor = user32.LoadCursorW(
                None,
                ctypes.cast(
                    IDC_ARROW,
                    wintypes.LPCWSTR
                )
            )

            wc.hbrBackground = None
            wc.lpszMenuName = None
            wc.lpszClassName = self.class_name

            result = user32.RegisterClassW(
                ctypes.byref(wc)
            )

            if not result:

                error = ctypes.get_last_error()

                if error != 1410:
                    raise ctypes.WinError(error)

            Canvas._class_registered = True

        # ----------------------------------------------------
        # Create window
        # ----------------------------------------------------

        self.hwnd = user32.CreateWindowExW(
            0,
            self.class_name,
            self.title,
            WS_OVERLAPPEDWINDOW,
            CW_USEDEFAULT,
            CW_USEDEFAULT,
            self.width,
            self.height,
            None,
            None,
            self.hinstance,
            None,
        )

        if not self.hwnd:
            raise ctypes.WinError(
                ctypes.get_last_error()
            )

    # ========================================================
    # API
    # ========================================================

    def show(self):
        """Show the Canvas window and start its event loop."""

        user32.ShowWindow(
            self.hwnd,
            SW_SHOW
        )

        user32.UpdateWindow(
            self.hwnd
        )

        self.running = True

        msg = wintypes.MSG()

        while self.running:

            result = user32.GetMessageW(
                ctypes.byref(msg),
                None,
                0,
                0
            )

            if result == -1:
                raise ctypes.WinError(
                    ctypes.get_last_error()
                )

            if result == 0:
                break

            user32.TranslateMessage(
                ctypes.byref(msg)
            )

            user32.DispatchMessageW(
                ctypes.byref(msg)
            )

    def close(self):
        """Close the Canvas window."""

        if not self.closed:
            user32.DestroyWindow(self.hwnd)

    def redraw(self):
        """Request the Canvas to redraw itself."""

        user32.InvalidateRect(
            self.hwnd,
            None,
            True
        )

    # ========================================================
    # Renderer hooks
    # ========================================================

    def on_draw(self, hdc):
        """
        Called whenever the Canvas needs to draw.

        A renderer can override this.
        """

        pass

    def on_resize(self, width, height):
        """
        Called whenever the Canvas is resized.
        """

        pass