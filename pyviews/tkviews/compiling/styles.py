from pyviews.compiling.attribute import compile_attr

def read_attributes(context):
    for attr in context.node.xml_node.items():
        (name, expr) = attr
        context.node.set_attr(name, expr)

def render_style(context):
    context.parent_node.context.styles[context.node.name] = context.node

def render_styles(context):
    context.parent_node.context.styles.update(context.node.get_styles())

def apply_style(node, style):
    styles = style.split(',')
    attrs = {}
    for style in styles:
        for key, value in node.context.styles[style].get_attrs().items():
            attrs[key] = value
    for attr in attrs.values():
        compile_attr(node, attr)