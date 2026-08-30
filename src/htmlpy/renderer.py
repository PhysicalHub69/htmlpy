import tkinter as tk
from pathlib import Path
from .dom import Element


NON_RENDERED_ELEMENTS = {
    "html",
    "head",
    "title",
    "meta",
    "link",
    "style",
    "script",
    "noscript",
    "base",
}


class Renderer:

    def __init__(
        self,
        width=800,
        height=600,
        title="htmlpy",
        stylesheets=None,
        base_path=None
    ):
        self.width = width
        self.height = height
        self.title = title
        self.stylesheets = stylesheets or []
        self.base_path = Path(base_path) if base_path else None

        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")

        # -----------------------------------------------------
        # Scrollable page
        # -----------------------------------------------------

        self.canvas = tk.Canvas(
            self.root,
            highlightthickness=0
        )

        self.scrollbar = tk.Scrollbar(
            self.root,
            orient="vertical",
            command=self.canvas.yview
        )

        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.scrollbar.pack(
            side="right",
            fill="y"
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.container = tk.Frame(
            self.canvas,
            bg="white"
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.container,
            anchor="nw"
        )

        self.container.bind(
            "<Configure>",
            self.on_container_configure
        )

        self.canvas.bind(
            "<Configure>",
            self.on_canvas_configure
        )

        # Mouse wheel scrolling.
        self.canvas.bind_all(
            "<MouseWheel>",
            self.on_mousewheel
        )

    # ---------------------------------------------------------
    # Scrolling
    # ---------------------------------------------------------

    def on_container_configure(self, event=None):
        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(
            self.canvas_window,
            width=event.width
        )

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    # ---------------------------------------------------------
    # CSS
    # ---------------------------------------------------------

    def get_styles(self, element):
        styles = {}

        for rule in self.stylesheets:
            selector = rule.selector

            if selector == element.tag:
                styles.update(
                    rule.properties
                )

            elif selector.startswith("."):
                class_name = element.attributes.get(
                    "class",
                    ""
                )

                if selector[1:] in class_name.split():
                    styles.update(
                        rule.properties
                    )

            elif selector.startswith("#"):
                element_id = element.attributes.get(
                    "id"
                )

                if selector[1:] == element_id:
                    styles.update(
                        rule.properties
                    )

        return styles

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def get_text(self, element):

        parts = []

        def collect(node):

            for child in node.children:

                if isinstance(child, str):
                    parts.append(child)

                elif isinstance(child, Element):
                    collect(child)

        collect(element)

        return "".join(parts).strip()

    def parse_font_size(
        self,
        styles,
        default=16
    ):

        value = styles.get(
            "font-size",
            f"{default}px"
        )

        try:
            return int(
                value.replace(
                    "px",
                    ""
                ).strip()
            )

        except ValueError:
            return default

    def get_color(self, styles):
        return styles.get(
            "color",
            "black"
        )

    def get_background(self, styles):
        return styles.get(
            "background-color",
            "white"
        )

    # ---------------------------------------------------------
    # Element rendering
    # ---------------------------------------------------------

    def render_element(
        self,
        element,
        parent
    ):

        tag = element.tag.lower()
        styles = self.get_styles(element)

        # -----------------------------------------------------
        # Non-visible document elements
        # -----------------------------------------------------

        if tag in NON_RENDERED_ELEMENTS:

            for child in element.children:

                if isinstance(child, Element):
                    self.render_element(
                        child,
                        parent
                    )

            return

        # -----------------------------------------------------
        # Headings
        # -----------------------------------------------------

        if tag in {
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6"
        }:

            sizes = {
                "h1": 32,
                "h2": 26,
                "h3": 22,
                "h4": 18,
                "h5": 16,
                "h6": 14,
            }

            font_size = self.parse_font_size(
                styles,
                sizes[tag]
            )

            label = tk.Label(
                parent,
                text=self.get_text(element),
                font=(
                    "Arial",
                    font_size,
                    "bold"
                ),
                fg=self.get_color(styles),
                bg=self.get_background(styles),
                anchor="w",
                justify="left"
            )

            label.pack(
                fill="x",
                padx=20,
                pady=(10, 5)
            )

        # -----------------------------------------------------
        # Paragraph / inline-ish text
        # -----------------------------------------------------

        elif tag in {
            "p",
            "span",
            "small",
            "mark",
            "del",
            "ins",
            "sub",
            "sup"
        }:

            font_size = self.parse_font_size(
                styles,
                16
            )

            label = tk.Label(
                parent,
                text=self.get_text(element),
                font=("Arial", font_size),
                fg=self.get_color(styles),
                bg=self.get_background(styles),
                anchor="w",
                justify="left",
                wraplength=self.width - 40
            )

            label.pack(
                fill="x",
                padx=20,
                pady=5
            )

        # -----------------------------------------------------
        # Bold / italic
        # -----------------------------------------------------

        elif tag in {
            "strong",
            "b",
            "em",
            "i"
        }:

            font_size = self.parse_font_size(
                styles,
                16
            )

            weight = (
                "bold"
                if tag in {
                    "strong",
                    "b"
                }
                else "normal"
            )

            slant = (
                "italic"
                if tag in {
                    "em",
                    "i"
                }
                else "roman"
            )

            label = tk.Label(
                parent,
                text=self.get_text(element),
                font=(
                    "Arial",
                    font_size,
                    weight,
                    slant
                ),
                fg=self.get_color(styles),
                bg=self.get_background(styles),
                anchor="w"
            )

            label.pack(
                fill="x",
                padx=20,
                pady=3
            )

        # -----------------------------------------------------
        # Links
        # -----------------------------------------------------

        elif tag == "a":

            link = tk.Label(
                parent,
                text=self.get_text(element),
                fg=(
                    self.get_color(styles)
                    if "color" in styles
                    else "blue"
                ),
                bg=self.get_background(styles),
                cursor="hand2",
                anchor="w",
                font=(
                    "Arial",
                    16,
                    "underline"
                )
            )

            link.pack(
                fill="x",
                padx=20,
                pady=4
            )

        # -----------------------------------------------------
        # Buttons
        # -----------------------------------------------------

        elif tag == "button":

            button = tk.Button(
                parent,
                text=self.get_text(element),
                font=("Arial", 14)
            )

            button.pack(
                anchor="w",
                padx=20,
                pady=8
            )

        # -----------------------------------------------------
        # Images
        # -----------------------------------------------------

        elif tag == "img":

            self.render_image(
                element,
                parent
            )

        # -----------------------------------------------------
        # Lists
        # -----------------------------------------------------

        elif tag in {
            "ul",
            "ol"
        }:

            list_frame = tk.Frame(
                parent,
                bg=self.get_background(styles)
            )

            list_frame.pack(
                fill="x",
                padx=20,
                pady=5
            )

            number = 1

            for child in element.children:

                if not isinstance(
                    child,
                    Element
                ):
                    continue

                if child.tag.lower() != "li":
                    continue

                prefix = (
                    f"{number}. "
                    if tag == "ol"
                    else "• "
                )

                label = tk.Label(
                    list_frame,
                    text=prefix + self.get_text(child),
                    font=("Arial", 16),
                    fg=self.get_color(styles),
                    bg=self.get_background(styles),
                    anchor="w"
                )

                label.pack(
                    fill="x"
                )

                number += 1

            return

        # -----------------------------------------------------
        # List item
        # -----------------------------------------------------

        elif tag == "li":
            return

        # -----------------------------------------------------
        # Input
        # -----------------------------------------------------

        elif tag == "input":

            input_type = element.attributes.get(
                "type",
                "text"
            ).lower()

            if input_type == "hidden":
                return

            entry = tk.Entry(
                parent,
                font=("Arial", 14)
            )

            placeholder = element.attributes.get(
                "placeholder"
            )

            if placeholder:
                entry.insert(
                    0,
                    placeholder
                )

            entry.pack(
                fill="x",
                padx=20,
                pady=5
            )

        # -----------------------------------------------------
        # Textarea
        # -----------------------------------------------------

        elif tag == "textarea":

            textarea = tk.Text(
                parent,
                height=6,
                font=("Arial", 14)
            )

            textarea.pack(
                fill="x",
                padx=20,
                pady=5
            )

        # -----------------------------------------------------
        # Label
        # -----------------------------------------------------

        elif tag == "label":

            label = tk.Label(
                parent,
                text=self.get_text(element),
                font=("Arial", 14),
                bg=self.get_background(styles),
                fg=self.get_color(styles),
                anchor="w"
            )

            label.pack(
                fill="x",
                padx=20,
                pady=3
            )

        # -----------------------------------------------------
        # Select
        # -----------------------------------------------------

        elif tag == "select":

            variable = tk.StringVar()

            option_values = []

            for child in element.children:

                if isinstance(
                    child,
                    Element
                ):

                    if child.tag.lower() == "option":
                        option_values.append(
                            self.get_text(child)
                        )

            if option_values:
                variable.set(
                    option_values[0]
                )

            option_menu = tk.OptionMenu(
                parent,
                variable,
                *option_values
            )

            option_menu.pack(
                anchor="w",
                padx=20,
                pady=5
            )

        # -----------------------------------------------------
        # Horizontal rule
        # -----------------------------------------------------

        elif tag == "hr":

            separator = tk.Frame(
                parent,
                height=2,
                bg="#cccccc"
            )

            separator.pack(
                fill="x",
                padx=20,
                pady=10
            )

        # -----------------------------------------------------
        # Line break
        # -----------------------------------------------------

        elif tag == "br":

            spacer = tk.Frame(
                parent,
                height=8
            )

            spacer.pack()

        # -----------------------------------------------------
        # Generic containers
        # -----------------------------------------------------

        elif tag in {
            "div",
            "section",
            "article",
            "main",
            "header",
            "footer",
            "nav",
            "aside",
            "figure",
            "figcaption",
            "form",
            "details",
            "summary"
        }:

            frame = tk.Frame(
                parent,
                bg=self.get_background(styles)
            )

            frame.pack(
                fill="x",
                expand=False
            )

            for child in element.children:

                if isinstance(
                    child,
                    Element
                ):

                    self.render_element(
                        child,
                        frame
                    )

            return

        # -----------------------------------------------------
        # Unknown elements
        # -----------------------------------------------------

        else:

            frame = tk.Frame(
                parent,
                bg=self.get_background(styles)
            )

            frame.pack(
                fill="x"
            )

            for child in element.children:

                if isinstance(
                    child,
                    Element
                ):

                    self.render_element(
                        child,
                        frame
                    )

            return

        # -----------------------------------------------------
        # Render children
        # -----------------------------------------------------

        for child in element.children:

            if isinstance(
                child,
                Element
            ):

                self.render_element(
                    child,
                    parent
                )

    # ---------------------------------------------------------
    # Image rendering
    # ---------------------------------------------------------

    def render_image(
        self,
        element,
        parent
    ):

        src = element.attributes.get(
            "src"
        )

        if not src:
            return

        if not self.base_path:
            return

        image_path = (
            self.base_path / src
        ).resolve()

        if not image_path.exists():
            return

        try:

            image = tk.PhotoImage(
                file=str(image_path)
            )

            label = tk.Label(
                parent,
                image=image
            )

            label.image = image

            label.pack(
                padx=20,
                pady=10,
                anchor="w"
            )

        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Render document
    # ---------------------------------------------------------

    def render(self, root):

        for element in root.children:

            if isinstance(
                element,
                Element
            ):

                self.render_element(
                    element,
                    self.container
                )

        # Make sure the scrollbar knows
        # the final document size.
        self.root.update_idletasks()

        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    # ---------------------------------------------------------
    # Run
    # ---------------------------------------------------------

    def run(self):
        self.root.mainloop()