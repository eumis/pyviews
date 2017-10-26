from pyviews.tk.widgets import WidgetNode

def bind(node: WidgetNode, event_name, command):
    node.bind(event_name, command)

def set_attr(node: WidgetNode, key, value):
    node.set_attr(key, value)

def grid_row_config(node: WidgetNode, key, value):
    node.widget.rowconfigure(int(key), **value)

def grid_column_config(node: WidgetNode, key, value):
    node.widget.columnconfigure(int(key), **value)
