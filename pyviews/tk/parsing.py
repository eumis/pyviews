from tkinter import Entry
from pyviews.core.xml import XmlAttr
from pyviews.core.node import NodeArgs
from pyviews.core.parsing import parse_attr
from pyviews.tk.widgets import WidgetNode, EntryWidget

def convert_to_node(inst, args: NodeArgs):
    if isinstance(inst, Entry):
        return EntryWidget(inst, args['xml_node'], args['parent_context'])
    return WidgetNode(inst, args['xml_node'], args['parent_context'])

def apply_text(node: WidgetNode):
    if not node.xml_node.text:
        return
    text_attr = XmlAttr(('text', node.xml_node.text))
    parse_attr(node, text_attr)
