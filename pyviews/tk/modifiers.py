from pyviews.tk.widgets import WidgetNode

def bind(node: WidgetNode, event_name, command):
    node.bind(event_name, command)

def bind_all(node: WidgetNode, event_name, command):
    node.bind_all(event_name, command)

def set_attr(node: WidgetNode, key, value):
    if key == 'style':
        keys = value.split(',') if isinstance(value, str) else value
        for key in [key for key in keys if key]:
            for item in node.globals[key]:
                item.apply(node)
    else:
        node.set_attr(key, value)

def config(node: WidgetNode, key, value):
    node.widget.config(**{key: value})

def visible(node: WidgetNode, key, value):
    if value:
        node.geometry.apply(node.widget)
    else:
        node.geometry.forget(node.widget)
