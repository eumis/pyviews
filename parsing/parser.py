import xml.etree.ElementTree as ET
from parsing.compiler import compile_view

def loadApp(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return compile_view(root)
    