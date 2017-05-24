from common.reflection.activator import create

def compile_view(node):
    return compile_node(node)

def compile_page(node, parent):
    compile_children(node, parent)

def compile_widget(node, parent):
    widget = compile_node(node, parent)
    apply_attributes(node, widget)
    apply_text(node, widget)
    compile_children(node, widget)

def apply_attributes(node, widget):
    for attr in node.items():
        apply_attr(widget, attr)

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

def apply_text(node, widget):
    text = node.text.strip()
    if text:
        widget.configure(text=text)

def compile_children(node, widget):
    for child in list(node):
        compile_widget(child, widget)

def compile_node(node, *args):
    # tag = "{namespace}name"
    typeDescription = node.tag.split('}')
    return create(typeDescription[0][1:], typeDescription[1], *args)
