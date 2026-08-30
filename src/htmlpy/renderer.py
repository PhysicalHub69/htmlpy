from .layout import layout
import sys
from pathlib import Path
import ctypes
from ctypes import wintypes

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from canvas import Canvas


class Renderer:
    def __init__(
        self,
        title="htmlpy",
        stylesheets=None,
        width=800,
        height=600,
        document=None,
    ):
        self.title = title
        self.stylesheets = stylesheets or []
        self.width = width
        self.height = height
        self.document = document

        self.layout = None
        self.canvas = None

    def build_layout(self, document=None):
        if document is not None:
            self.document = document

        if self.document is None:
            raise ValueError("No document provided")

        self.layout = layout(
            self.document,
            self.width,
            self.height,
        )

        return self.layout

    def render(self, document=None):
        return self.build_layout(document)

    def run(self, document=None):
        if document is not None:
            self.document = document

        if self.document is None:
            raise ValueError("No document provided")

        self.build_layout()

        self.canvas = Canvas(
            title=self.title,
            width=self.width,
            height=self.height,
        )

        self.canvas.on_draw = self._draw
        self.canvas.show()

    # ========================================================
    # Drawing
    # ========================================================

    def _draw(self, hdc):
        if self.layout is None:
            return

        self._draw_box(hdc, self.layout)

    def _draw_box(self, hdc, box):
        node = box.node

        rect = box.rect

        # ----------------------------------------------------
        # Background
        # ----------------------------------------------------

        background = self._style(
            node,
            "background-color",
            None,
        )

        if background:
            self._fill_rect(
                hdc,
                rect.x,
                rect.y,
                rect.width,
                rect.height,
                background,
            )

        # ----------------------------------------------------
        # Borders
        # ----------------------------------------------------

        border_width = self._style(
            node,
            "border-width",
            None,
        )

        border_color = self._style(
            node,
            "border-color",
            None,
        )

        if border_width and border_color:
            self._draw_border(
                hdc,
                rect.x,
                rect.y,
                rect.width,
                rect.height,
                border_width,
                border_color,
            )

        # ----------------------------------------------------
        # Text
        # ----------------------------------------------------

        text = getattr(node, "text", None)

        if text is not None:
            text = str(text)

            if text.strip():
                self._draw_text(
                    hdc,
                    text,
                    rect.x,
                    rect.y,
                    node,
                )

        # ----------------------------------------------------
        # Children
        # ----------------------------------------------------

        for child in box.children:
            self._draw_box(hdc, child)

    # ========================================================
    # Styles
    # ========================================================

    def _style(self, node, name, default=None):
        styles = getattr(node, "styles", None)

        if isinstance(styles, dict):
            return styles.get(name, default)

        return default

    # ========================================================
    # Text
    # ========================================================

    def _draw_text(
        self,
        hdc,
        text,
        x,
        y,
        node,
    ):
        gdi32 = ctypes.windll.gdi32

        color = self._style(
            node,
            "color",
            "#000000",
        )

        rgb = self._parse_color(color)

        if rgb is not None:
            gdi32.SetTextColor(
                hdc,
                self._rgb(*rgb),
            )

        gdi32.SetBkMode(
            hdc,
            1,
        )

        font = self._create_font(node)

        old_font = None

        if font:
            old_font = gdi32.SelectObject(
                hdc,
                font,
            )

        # Handle multiline text.
        lines = text.splitlines()

        if not lines:
            lines = [""]

        line_height = self._font_size(node) + 4

        for index, line in enumerate(lines):
            gdi32.TextOutW(
                hdc,
                int(x),
                int(y + index * line_height),
                line,
                len(line),
            )

        if old_font:
            gdi32.SelectObject(
                hdc,
                old_font,
            )

        if font:
            gdi32.DeleteObject(font)

    # ========================================================
    # Fonts
    # ========================================================

    def _font_size(self, node):
        value = self._style(
            node,
            "font-size",
            "16px",
        )

        try:
            return float(
                str(value)
                .replace("px", "")
                .strip()
            )
        except ValueError:
            return 16

    def _create_font(self, node):
        gdi32 = ctypes.windll.gdi32

        size = self._font_size(node)

        weight = self._style(
            node,
            "font-weight",
            "normal",
        )

        if str(weight).lower() in (
            "bold",
            "700",
            "800",
            "900",
        ):
            font_weight = 700
        else:
            font_weight = 400

        italic = self._style(
            node,
            "font-style",
            "normal",
        )

        is_italic = 1 if str(italic).lower() == "italic" else 0

        return gdi32.CreateFontW(
            -int(size),
            0,
            0,
            0,
            font_weight,
            is_italic,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            "Arial",
        )

    # ========================================================
    # Rectangles
    # ========================================================

    def _fill_rect(
        self,
        hdc,
        x,
        y,
        width,
        height,
        color,
    ):
        rgb = self._parse_color(color)

        if rgb is None:
            return

        gdi32 = ctypes.windll.gdi32

        brush = gdi32.CreateSolidBrush(
            self._rgb(*rgb)
        )

        rect = wintypes.RECT(
            int(x),
            int(y),
            int(x + width),
            int(y + height),
        )

        gdi32.FillRect(
            hdc,
            ctypes.byref(rect),
            brush,
        )

        gdi32.DeleteObject(
            brush
        )

    def _draw_border(
        self,
        hdc,
        x,
        y,
        width,
        height,
        border_width,
        color,
    ):
        rgb = self._parse_color(color)

        if rgb is None:
            return

        try:
            thickness = max(
                1,
                int(
                    str(border_width)
                    .replace("px", "")
                    .strip()
                ),
            )
        except ValueError:
            thickness = 1

        gdi32 = ctypes.windll.gdi32

        pen = gdi32.CreatePen(
            0,
            thickness,
            self._rgb(*rgb),
        )

        old_pen = gdi32.SelectObject(
            hdc,
            pen,
        )

        old_brush = gdi32.SelectObject(
            hdc,
            gdi32.GetStockObject(5),
        )

        gdi32.Rectangle(
            hdc,
            int(x),
            int(y),
            int(x + width),
            int(y + height),
        )

        gdi32.SelectObject(
            hdc,
            old_pen,
        )

        gdi32.SelectObject(
            hdc,
            old_brush,
        )

        gdi32.DeleteObject(
            pen
        )

    # ========================================================
    # Colors
    # ========================================================

    @staticmethod
    def _parse_color(value):
        if not value:
            return None

        value = str(value).strip().lower()

        named = {
            "black": (0, 0, 0),
            "white": (255, 255, 255),
            "red": (255, 0, 0),
            "green": (0, 128, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "gray": (128, 128, 128),
            "grey": (128, 128, 128),
            "orange": (255, 165, 0),
            "purple": (128, 0, 128),
            "transparent": None,
        }

        if value in named:
            return named[value]

        if value.startswith("#"):
            value = value[1:]

            if len(value) == 3:
                value = "".join(
                    c + c
                    for c in value
                )

            if len(value) == 6:
                try:
                    return (
                        int(value[0:2], 16),
                        int(value[2:4], 16),
                        int(value[4:6], 16),
                    )
                except ValueError:
                    return None

        return None

    @staticmethod
    def _rgb(r, g, b):
        return (
            r
            | (g << 8)
            | (b << 16)
        )