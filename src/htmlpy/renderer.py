import tkinter as tk
from .dom import Element
from .css import CSSRule


class Renderer:

    def __init__(self, width=800, height=600, title="htmlpy", stylesheets=None):
        self.width = width
        self.height = height
        self.title = title
        self.stylesheets = stylesheets or []

        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")

        self.canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            bg="white"
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        self.y = 20

    def get_styles(self, element):
        styles = {}

        for rule in self.stylesheets:
            selector = rule.selector

            # Element selector: h1, p, button, etc.
            if selector == element.tag:
                styles.update(rule.properties)

            # Class selector: .thing
            elif selector.startswith("."):
                class_name = element.attributes.get("class", "")

                if selector[1:] in class_name.split():
                    styles.update(rule.properties)

            # ID selector: #thing
            elif selector.startswith("#"):
                element_id = element.attributes.get("id")

                if selector[1:] == element_id:
                    styles.update(rule.properties)

        return styles

    def draw(self, element):

        styles = self.get_styles(element)

        if element.tag == "h1":

            font_size = int(
                styles.get("font-size", "28px").replace("px", "")
            )

            color = styles.get("color", "black")

            self.canvas.create_text(
                20,
                self.y,
                text=element.text(),
                anchor="nw",
                font=("Arial", font_size, "bold"),
                fill=color
            )

            self.y += font_size + 30

        elif element.tag == "h2":

            font_size = int(
                styles.get("font-size", "22px").replace("px", "")
            )

            color = styles.get("color", "black")

            self.canvas.create_text(
                20,
                self.y,
                text=element.text(),
                anchor="nw",
                font=("Arial", font_size, "bold"),
                fill=color
            )

            self.y += font_size + 25

        elif element.tag == "p":

            font_size = int(
                styles.get("font-size", "16px").replace("px", "")
            )

            color = styles.get("color", "black")

            self.canvas.create_text(
                20,
                self.y,
                text=element.text(),
                anchor="nw",
                font=("Arial", font_size),
                fill=color
            )

            self.y += font_size + 20

        elif element.tag == "button":

            button = tk.Button(
                self.root,
                text=element.text(),
                font=("Arial", 14)
            )

            self.canvas.create_window(
                20,
                self.y,
                anchor="nw",
                window=button
            )

            self.y += 50

        for child in element.children:

            if isinstance(child, Element):
                self.draw(child)

    def render(self, root):
        for element in root.children:

            if isinstance(element, Element):
                self.draw(element)

    def run(self):
        self.root.mainloop()