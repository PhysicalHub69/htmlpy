from html.parser import HTMLParser
from pathlib import Path
from .css import parse_css

from .dom import Element


class Parser(HTMLParser):

    def __init__(self, base_path=None):
        super().__init__()

        self.root = Element("root")
        self.stack = [self.root]
        self.base_path = Path(base_path) if base_path else None
        self.stylesheets = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        element = Element(
            tag,
            attributes
        )

        self.stack[-1].append(element)

        # Automatically load external CSS.
        if tag.lower() == "link":
            if attributes.get("rel", "").lower() == "stylesheet":
                href = attributes.get("href")

                if href:
                    self.load_stylesheet(href)

        if tag.lower() not in {
            "area", "base", "br", "col",
            "embed", "hr", "img", "input",
            "link", "meta", "param", "source",
            "track", "wbr"
        }:
            self.stack.append(element)

    def handle_startendtag(self, tag, attrs):
        element = Element(
            tag,
            dict(attrs)
        )

        self.stack[-1].append(element)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                break

    def handle_data(self, data):
        if data:
            self.stack[-1].append(data)

    def load_stylesheet(self, href):
        if not self.base_path:
            return

        css_path = (self.base_path / href).resolve()

        if not css_path.exists():
            raise FileNotFoundError(
                f"Stylesheet not found: {css_path}"
            )

        css = css_path.read_text(
            encoding="utf-8"
        )

        self.stylesheets.extend(parse_css(css))


def parse(html, base_path=None):
    parser = Parser(base_path)
    parser.feed(html)

    return parser.root, parser.stylesheets