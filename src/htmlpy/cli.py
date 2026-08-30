import sys
from pathlib import Path

from .parser import parse
from .renderer import Renderer


def main():

    if len(sys.argv) < 2:
        print("Usage: htmlpy <html file>")
        return

    filename = Path(sys.argv[1])

    if not filename.exists():
        print(f"File not found: {filename}")
        return

    if filename.suffix.lower() not in {".html", ".htm"}:
        print("htmlpy expects an HTML file.")
        return

    html = filename.read_text(
        encoding="utf-8"
    )

    document, stylesheets = parse(
        html,
        filename.parent
    )

    renderer = Renderer(
        title=filename.stem,
        stylesheets=stylesheets
    )

    renderer.render(document)
    renderer.run()