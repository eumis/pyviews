from common.reflection.activator import create

def compile_view(node):
    return compile_node(node)

def compile_page(node, parent):
    for child in list(node):
        compile_widget(child, parent)

def compile_widget(node, parent):
    widget = compile_node(node, parent)
    for attr in node.items():
        apply_attr(widget, attr)
    text = node.text.strip()
    if text:
        widget.configure(text=text)
    for child in list(node):
        compile_widget(child, widget)

def apply_attr(widget, attr):
    if not hasattr(widget, attr[0]):
        return
    item = getattr(widget, attr[0])
    if callable(item):
        apply_method(widget, attr)
    else:
        apply_property(widget, attr)

def apply_method(widget, attr):
    exec('widget.' + attr[0] + "(" + attr[1] + ")")

def apply_property(widget, attr):
    widget.__dict__[attr[0]] = attr[1]

def compile_node(node, *args):
    # tag = "{namespace}name"
    typeDescription = node.tag.split('}')
    return create(typeDescription[0][1:], typeDescription[1], *args)
