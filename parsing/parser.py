import xml.etree.ElementTree as ET
from parsing.compiler import compile_view, compile_page

def loadApp(path):
    root = loadRoot(path)
    return compile_view(root)

def loadPage(path, parent):
    page = loadRoot(path)
    return compile_page(page, parent)

def loadRoot(path):
    tree = ET.parse(path)
    return tree.getroot()
   