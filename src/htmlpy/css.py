import re


def parse_css(css_text):
    """
    Parse basic CSS declarations into a dictionary.

    Example:

        body {
            width: 800px;
            margin: 10px;
        }

    becomes:

        {
            "body": {
                "width": "800px",
                "margin": "10px"
            }
        }
    """

    rules = {}

    # Remove comments
    css_text = re.sub(
        r"/\*.*?\*/",
        "",
        css_text,
        flags=re.DOTALL,
    )

    pattern = re.compile(
        r"([^{}]+)\{([^{}]*)\}"
    )

    for selector, declarations in pattern.findall(css_text):
        selector = selector.strip()

        styles = {}

        for declaration in declarations.split(";"):
            if ":" not in declaration:
                continue

            name, value = declaration.split(":", 1)

            name = name.strip().lower()
            value = value.strip()

            if name and value:
                styles[name] = value

        if styles:
            rules[selector] = styles

    return rules


def apply_styles(node, rules):
    """
    Apply matching CSS rules to a DOM node.
    """

    if not getattr(node, "styles", None):
        node.styles = {}

    tag = getattr(node, "tag", None)

    if tag in rules:
        node.styles.update(rules[tag])

    attributes = getattr(node, "attributes", {})

    element_id = attributes.get("id")

    if element_id:
        selector = f"#{element_id}"

        if selector in rules:
            node.styles.update(rules[selector])

    classes = attributes.get("class", "")

    for class_name in classes.split():
        selector = f".{class_name}"

        if selector in rules:
            node.styles.update(rules[selector])

    for child in getattr(node, "children", []):
        apply_styles(child, rules)

    return node