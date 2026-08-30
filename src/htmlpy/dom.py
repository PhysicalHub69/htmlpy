class Node:
    def __init__(
        self,
        tag=None,
        attributes=None,
        children=None,
        text=None,
    ):
        self.tag = tag
        self.attributes = attributes or {}
        self.children = children or []
        self.text = text
        self.styles = {}

    def append(self, child):
        self.children.append(child)

    def append_child(self, child):
        self.children.append(child)

    def set_style(self, name, value):
        self.styles[name] = value

    def get_style(self, name, default=None):
        return self.styles.get(name)

    def __repr__(self):
        return f"<Node {self.tag!r}>"


class Element(Node):
    """HTML element used by parser.py."""
    pass


class Document(Node):
    def __init__(self):
        super().__init__(
            tag="document",
            attributes={},
            children=[],
        )