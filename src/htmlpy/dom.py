class Element:
    def __init__(self, tag, attributes=None, children=None):
        self.tag = tag
        self.attributes = attributes or {}
        self.children = children or []

    def append(self, child):
        self.children.append(child)

    def text(self):
        return "".join(
            child if isinstance(child, str) else child.text()
            for child in self.children
        ).strip()

    def get_attribute(self, name, default=None):
        return self.attributes.get(name, default)