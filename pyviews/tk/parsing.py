from pyviews.core.parsing import NodeArgs
from pyviews.tk.widgets import WidgetNode

def convert_to_node(inst, args: NodeArgs):
    return WidgetNode(inst, args['xml_node'], args['parent_globals'])
