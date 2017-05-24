import xml.etree.ElementTree as ET
from parsing.compiler import compile_view

def load_view(path, parent=None):
    page = load_root(path)
    return compile_view(page, parent)

def load_root(path):
    tree = ET.parse(path)
    return tree.getroot()
   