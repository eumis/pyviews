from pyviews.view.geometry import GridGeometry, PackGeometry
from pyviews.binding.expressions import parse_dictionary

def grid(node, attr):
    (key, value) = attr
    if not node.geometry:
        node.geometry = GridGeometry()
    node.geometry.set(key, value)

def pack(node, attr):
    (key, value) = attr
    if not node.geometry:
        node.geometry = PackGeometry()
    node.geometry.set(key, value)

def config(node, attr):
    (key, value) = attr
    node.config(key, value)

def row_config(node, attr):
    (key, value) = attr
    if isinstance(value, str):
        value = parse_dictionary(value)
    node.row_config(int(key[1:]), value)

def col_config(node, attr):
    (key, value) = attr
    if isinstance(value, str):
        value = parse_dictionary(value)
    node.col_config(int(key[1:]), value)
