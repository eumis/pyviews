from pyviews.view.geometry import GridGeometry, PackGeometry

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

def style(node, attr):
    applies = [attr[1]] if callable(attr[1]) else attr[1]
    for apply in applies:
        apply(node.get_widget())
