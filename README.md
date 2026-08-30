# htmlpy

htmlpy is a Python-based application framework which attempts to use HTML and CSS for desktop applications.

The goal is to allow desktop applications to be built using familiar web technologies, without the requirement to run inside a normal web browser.

## Current Status

htmlpy is currently in early development.

Current functionality includes: HTML parsing Basic DOM representation CSS parsing CSS stylesheet loading Desktop window rendering HTML-to-Python generation Command-line interfaceCSS parsing is currently implemented, but CSS styling is not yet fully applied to rendered elements.

## Installation

Clone the repository and install htmlpy in editable mode:

```powershell
py -m pip install -e .
```

After installation, the `htmlpy` command should be available.

## Usage

Given an HTML file:

```text
index.html
```

run:

```powershell
htmlpy index.html
```

This generates a Python file from the HTML document.

For example:

```text
index.html  ↓
index.py
```

The generated Python application can then be run normally with Python.

## CSS

CSS files can be referenced by HTML documents, and parsed by htmlpy.

Example project:

```text
my-project/
├── index.html
└── style.css
```

Example HTML:

```html
<!DOCTYPE html>
Hello, htmlpy!
```

htmlpy detects the referenced stylesheet, and passes it through the CSS parser.

Full CSS application to DOM elements is still under development.

## Exporting Applications

A planned feature of htmlpy is direct executable exporting:

```powershell
htmlpy index.html -e
```

This will package the application as a standalone executable.

The output filename can be specified with `-o`:

```powershell
htmlpy index.html -e -o MyGame.exe
```

A custom application icon can be specified with `-i`:

```powershell
htmlpy index.html -e -i my-icon.ico
```

Both options can be used together:

```powershell
htmlpy index.html -e -o MyGame.exe -i my-icon.ico
```

Executable exporting is still under development, and should not be considered stable until implemented.

## Project Structure
```texthtmlpy/

├── src/
│  └── htmlpy/
│    ├── __init__.py
│    ├── __main__.py
│    ├── cli.py
│    ├── css.py
│    ├── dom.py
│    ├── parser.py
│    └── renderer.py
├── .gitignore
├── LICENSE
├── pyproject.toml
└── README.md
```

## Development

Install the project in editable mode:

```powershell
py -m pip install -e .
```

Changes made inside `src/htmlpy/` will then be reflected immediately when using the installed package.

## Long-Term Goals

The long-term goal of htmlpy is to provide a complete desktop application framework based around HTML and CSS.

Potential features include: Full CSS styling More complete HTML support JavaScript support Native desktop application packaging Standalone executable generation Custom application names and icons Cross-platform application builds Persistent application data and save files Additional native APIs accessible from HTML applicationshtmlpy is experimental software and its API and behavior may change significantly during development.