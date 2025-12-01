from xml.etree.ElementTree import Element, SubElement, tostring
from typing import Any, List, Tuple, Union

def emit_value(parent, value):
    """
    Рекурсивно создаёт XML для любого значения:
    - число / строка
    - массив
    """
    if isinstance(value, list):
        arr_el = SubElement(parent, "array")
        for v in value:
            emit_value(arr_el, v)
    elif isinstance(value, int):
        el = SubElement(parent, "number")
        el.text = str(value)
    elif isinstance(value, str):
        el = SubElement(parent, "string")
        el.text = value
    else:
        el = SubElement(parent, "value")
        el.text = str(value)

def emit_xml(nodes: List[Tuple[str, str, Any]]) -> str:
    """
    nodes = [("const", name, value), ("value", value), ...]
    """
    root = Element("root")
    for n in nodes:
        kind = n[0]
        if kind == "const":
            name = n[1]
            value = n[2]
            const_el = SubElement(root, f"const_{name}")
            emit_value(const_el, value)
        elif kind == "value":
            value = n[1]
            value_el = SubElement(root, "value")
            emit_value(value_el, value)
        else:
            # на всякий случай
            other_el = SubElement(root, "node")
            emit_value(other_el, n)
    # Возвращаем красивый XML
    return tostring(root, encoding="unicode")
