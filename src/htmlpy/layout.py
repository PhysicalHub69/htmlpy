from dataclasses import dataclass, field
from typing import Any


@dataclass
class Rect:
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0


@dataclass
class LayoutBox:
    node: Any
    rect: Rect = field(default_factory=Rect)
    children: list["LayoutBox"] = field(default_factory=list)

    margin_top: float = 0
    margin_right: float = 0
    margin_bottom: float = 0
    margin_left: float = 0

    padding_top: float = 0
    padding_right: float = 0
    padding_bottom: float = 0
    padding_left: float = 0


def parse_size(value, parent_size=0):
    if value is None:
        return 0

    value = str(value).strip()

    if value.endswith("px"):
        try:
            return float(value[:-2])
        except ValueError:
            return 0

    if value.endswith("%"):
        try:
            return parent_size * float(value[:-1]) / 100
        except ValueError:
            return 0

    try:
        return float(value)
    except ValueError:
        return 0


def get_style(node, name, default=None):
    styles = getattr(node, "styles", None)

    if isinstance(styles, dict):
        return styles.get(name, default)

    return default


def make_layout_tree(node):
    box = LayoutBox(node=node)

    children = getattr(node, "children", [])

    for child in children:
        box.children.append(make_layout_tree(child))

    return box


def layout_tree(box, x=0, y=0, width=800):
    node = box.node

    margin = parse_size(get_style(node, "margin", 0), width)
    padding = parse_size(get_style(node, "padding", 0), width)

    box.margin_top = parse_size(
        get_style(node, "margin-top", margin), width
    )
    box.margin_right = parse_size(
        get_style(node, "margin-right", margin), width
    )
    box.margin_bottom = parse_size(
        get_style(node, "margin-bottom", margin), width
    )
    box.margin_left = parse_size(
        get_style(node, "margin-left", margin), width
    )

    box.padding_top = parse_size(
        get_style(node, "padding-top", padding), width
    )
    box.padding_right = parse_size(
        get_style(node, "padding-right", padding), width
    )
    box.padding_bottom = parse_size(
        get_style(node, "padding-bottom", padding), width
    )
    box.padding_left = parse_size(
        get_style(node, "padding-left", padding), width
    )

    specified_width = get_style(node, "width")

    if specified_width is not None:
        content_width = parse_size(specified_width, width)
    else:
        content_width = max(
            0,
            width
            - box.margin_left
            - box.margin_right
            - box.padding_left
            - box.padding_right,
        )

    box.rect.x = x + box.margin_left
    box.rect.y = y + box.margin_top
    box.rect.width = content_width

    display = get_style(node, "display", "block")

    if display == "none":
        box.rect.width = 0
        box.rect.height = 0
        return box

    current_y = (
        box.rect.y
        + box.padding_top
    )

    for child in box.children:
        child_width = max(
            0,
            content_width
            - box.padding_left
            - box.padding_right,
        )

        layout_tree(
            child,
            box.rect.x + box.padding_left,
            current_y,
            child_width,
        )

        current_y = (
            child.rect.y
            + child.rect.height
            + child.margin_bottom
        )

    specified_height = get_style(node, "height")

    if specified_height is not None:
        content_height = parse_size(specified_height, 0)
    else:
        content_height = max(
            0,
            current_y
            - box.rect.y
            + box.padding_bottom,
        )

    box.rect.height = content_height

    return box


def layout(node, width=800, height=600):
    tree = make_layout_tree(node)
    layout_tree(tree, 0, 0, width)

    if tree.rect.height < height:
        tree.rect.height = height

    return tree