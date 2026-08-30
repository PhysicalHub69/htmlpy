from pathlib import Path
import shutil
import re


def find_assets_folder(root: Path):
    """Find the first folder whose name ends with _files."""
    for folder in root.iterdir():
        if folder.is_dir() and folder.name.endswith("_files"):
            return folder

    return None


def find_css_files(assets_folder: Path):
    """Find all CSS files inside the assets folder."""
    return list(assets_folder.rglob("*.css"))


def rewrite_stylesheets(html: str, css_files, assets_folder: Path):
    """Replace stylesheet URLs with local CSS paths."""

    for css_file in css_files:
        relative = css_file.relative_to(assets_folder.parent)
        local_path = relative.as_posix()

        # Match href="..." and href='...'
        pattern = (
            r'(<link\b[^>]*?\bhref\s*=\s*[\'"])([^\'"]+)([\'"])'
        )

        def replace(match):
            href = match.group(2)

            # Match the CSS filename against the original href
            if Path(href.split("?")[0]).name == css_file.name:
                return match.group(1) + local_path + match.group(3)

            return match.group(0)

        html = re.sub(pattern, replace, html, flags=re.IGNORECASE)

    return html


def copy_assets(assets_folder: Path, output_root: Path):
    """Copy the entire _files folder into the output directory."""
    destination = output_root / assets_folder.name

    if destination.exists():
        shutil.rmtree(destination)

    shutil.copytree(assets_folder, destination)

    return destination


def build(input_file: str, output_file: str | None = None):
    input_path = Path(input_file).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    root = input_path.parent

    if output_file is None:
        output_path = root / f"{input_path.stem}_htmlpy{input_path.suffix}"
    else:
        output_path = Path(output_file).resolve()

    assets_folder = find_assets_folder(root)

    if assets_folder is None:
        print("No *_files folder found.")
        shutil.copy2(input_path, output_path)
        return

    print(f"Found assets folder: {assets_folder.name}")

    css_files = find_css_files(assets_folder)

    print(f"Found {len(css_files)} CSS file(s):")

    for css in css_files:
        print(f"  - {css.name}")

    # Read HTML
    html = input_path.read_text(encoding="utf-8", errors="replace")

    # Copy assets beside the generated HTML
    output_root = output_path.parent
    copy_assets(assets_folder, output_root)

    # Rewrite CSS references
    html = rewrite_stylesheets(
        html,
        css_files,
        assets_folder
    )

    # Write generated HTML
    output_path.write_text(
        html,
        encoding="utf-8"
    )

    print(f"Built: {output_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m htmlpy <file.html>")
        sys.exit(1)

    build(sys.argv[1])