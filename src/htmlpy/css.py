class CSSRule:
    def __init__(self, selector, properties):
        self.selector = selector.strip()
        self.properties = properties


def parse_css(css):
    rules = []

    for block in css.split("}"):
        if "{" not in block:
            continue

        selector, body = block.split("{", 1)

        properties = {}

        for declaration in body.split(";"):
            if ":" not in declaration:
                continue

            name, value = declaration.split(":", 1)

            properties[name.strip()] = value.strip()

        rules.append(
            CSSRule(selector, properties)
        )

    return rules