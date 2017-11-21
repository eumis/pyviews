from pyviews.tk.widgets import WidgetNode

def bind(node: WidgetNode, event_name, command):
    node.bind(event_name, command)

def bind_all(node: WidgetNode, event_name, command):
    node.bind_all(event_name, command)

def set_attr(node: WidgetNode, key, value):
    node.set_attr(key, value)

def config(node: WidgetNode, key, value):
    node.widget.config(**{key: value})
