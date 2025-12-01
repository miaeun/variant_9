import xml.etree.ElementTree as ET
from typing import Any, List, Tuple

def to_xml_node(parent, name, value):
    if isinstance(value, list):
        arr_el = ET.SubElement(parent, name)
        for i, v in enumerate(value):
            to_xml_node(arr_el, "item", v)
    elif isinstance(value, str):
        el = ET.SubElement(parent, name)
        el.text = value
    elif isinstance(value, int) or isinstance(value, float):
        el = ET.SubElement(parent, name)
        el.text = str(value)
    else:
        el = ET.SubElement(parent, name)
        el.text = str(value)

def emit_xml(output_nodes):
    root = ET.Element("config")
    for node in output_nodes:
        if node[0]=="const":
            _, name, value = node
            to_xml_node(root, f"const_{name}", value)
        else:
            _, value = node
            to_xml_node(root, "value", value)
    return ET.tostring(root, encoding="utf-8").decode("utf-8")
