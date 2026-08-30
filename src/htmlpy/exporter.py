from pathlib import Path
import subprocess
import sys
import tempfile
import shutil


def export_exe(input_file, output=None, icon=None):
    input_path = Path(input_file).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    if input_path.suffix.lower() not in {".html", ".htm"}:
        raise ValueError("Input file must be an HTML file.")

    output_path = (
        Path(output).resolve()
        if output
        else input_path.with_suffix(".exe")
    )

    icon_path = None

    if icon:
        icon_path = Path(icon).resolve()

        if not icon_path.exists():
            raise FileNotFoundError(
                f"Icon file not found: {icon_path}"
            )

        if icon_path.suffix.lower() != ".ico":
            raise ValueError("Icon file must be an .ico file.")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        script_path = temp_path / "main.py"

        html = input_path.read_text(
            encoding="utf-8"
        )

        script = f'''from htmlpy.parser import parse
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

        script_path.write_text(
            script,
            encoding="utf-8"
        )

        command = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            "--windowed",
            "--name",
            output_path.stem,
        ]

        if icon_path:
            command.extend([
                "--icon",
                str(icon_path),
            ])

        command.append(str(script_path))

        subprocess.run(
            command,
            check=True,
            cwd=temp_path
        )

        built_exe = (
            temp_path
            / "dist"
            / f"{output_path.stem}.exe"
        )

        if not built_exe.exists():
            raise RuntimeError(
                "PyInstaller did not produce the expected executable."
            )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        shutil.copy2(
            built_exe,
            output_path
        )

    print(f"Created: {output_path}")