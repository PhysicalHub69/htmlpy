from html.parser import HTMLParser
from pathlib import Path

from .css import parse_css
from .dom import Element


VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


class Parser(HTMLParser):

    def __init__(self, base_path=None):
        super().__init__(
            convert_charrefs=True
        )

        self.root = Element("root")
        self.stack = [self.root]

        self.base_path = (
            Path(base_path).resolve()
            if base_path
            else None
        )

        self.stylesheets = []

    def handle_decl(self, decl):
        # Handles <!DOCTYPE html>.
        # It is intentionally not added to the DOM.
        pass

    def handle_starttag(self, tag, attrs):

        tag = tag.lower()
        attributes = dict(attrs)

        element = Element(
            tag,
            attributes
        )

        self.stack[-1].append(
            element
        )

        # Automatically load external CSS.
        if tag == "link":

            if (
                attributes.get(
                    "rel",
                    ""
                ).lower()
                == "stylesheet"
            ):

                href = attributes.get(
                    "href"
                )

                if href:
                    self.load_stylesheet(
                        href
                    )

        if tag not in VOID_ELEMENTS:
            self.stack.append(
                element
            )

    def handle_startendtag(
        self,
        tag,
        attrs
    ):

        element = Element(
            tag.lower(),
            dict(attrs)
        )

        self.stack[-1].append(
            element
        )

    def handle_endtag(self, tag):

        tag = tag.lower()

        # Find the matching open element.
        for index in range(
            len(self.stack) - 1,
            0,
            -1
        ):

            if (
                self.stack[index].tag
                == tag
            ):

                self.stack = (
                    self.stack[:index]
                )

                break

    def handle_data(self, data):

        if data:
            self.stack[-1].append(
                data
            )

    def handle_comment(self, data):
        # Comments don't need to exist
        # in the rendered DOM for now.
        pass

    def load_stylesheet(self, href):

        if not self.base_path:
            return

        css_path = (
            self.base_path / href
        ).resolve()

        if not css_path.exists():

            raise FileNotFoundError(
                f"Stylesheet not found: "
                f"{css_path}"
            )

        css = css_path.read_text(
            encoding="utf-8"
        )

        self.stylesheets.extend(
            parse_css(css)
        )


def parse(
    html,
    base_path=None
):

    parser = Parser(
        base_path
    )

    parser.feed(html)
    parser.close()

    return (
        parser.root,
        parser.stylesheets
    )