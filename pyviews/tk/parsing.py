from tkinter import Entry
from tkinter.ttk import Widget as TtkWidget
from pyviews.core.xml import XmlAttr
from pyviews.core.node import NodeArgs
from pyviews.core.parsing import parse_attr
from pyviews.tk.widgets import WidgetNode, EntryWidget
from pyviews.tk.ttk import TtkWidgetNode

def convert_to_node(inst, args: NodeArgs):
    args = (inst, args['xml_node'], args['parent_context'])
    if isinstance(inst, Entry):
        return EntryWidget(*args)
    if isinstance(inst, TtkWidget):
        return TtkWidgetNode(*args)
    return WidgetNode(*args)

def apply_text(node: WidgetNode):
    if not node.xml_node.text:
        return
    text_attr = XmlAttr(('text', node.xml_node.text))
    parse_attr(node, text_attr)
