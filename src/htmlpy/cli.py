import argparse
from pathlib import Path

from .exporter import export_exe


def build_python(input_file):
    input_path = Path(input_file).resolve()

    if not input_path.exists():
        raise FileNotFoundError(
            f"File not found: {input_file}"
        )

    if input_path.suffix.lower() not in {".html", ".htm"}:
        raise ValueError("Input file must be an HTML file.")

    html = input_path.read_text(
        encoding="utf-8"
    )

    output_path = input_path.with_suffix(".py")

    code = f'''from htmlpy.parser import parse
from htmlpy.renderer import Renderer

html = {html!r}

root, stylesheets = parse(
    html,
    base_path={str(input_path.parent)!r}
)

renderer = Renderer(
    title={input_path.stem!r},
    stylesheets=stylesheets
)

renderer.render(root)
renderer.run()
'''

    output_path.write_text(
        code,
        encoding="utf-8"
    )

    print(f"Created: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        prog="htmlpy",
        description="Build HTML applications with htmlpy."
    )

    parser.add_argument(
        "input",
        help="HTML file to build"
    )

    parser.add_argument(
        "-e",
        "--exe",
        action="store_true",
        help="Export the application as an executable"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output filename"
    )

    parser.add_argument(
        "-i",
        "--icon",
        help="Application icon (.ico)"
    )

    args = parser.parse_args()

    try:
        if args.exe:
            export_exe(
                args.input,
                output=args.output,
                icon=args.icon
            )
        else:
            if args.output:
                parser.error("-o can only be used with -e")

            if args.icon:
                parser.error("-i can only be used with -e")

            build_python(args.input)

    except (FileNotFoundError, ValueError, RuntimeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()