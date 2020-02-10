"""Once binding"""

from pyviews.binding import BindingContext
from pyviews.compilation import execute


def run_once(context: BindingContext):
    value = execute(context.expression_body, context.node.node_globals.to_dictionary())
    context.setter(context.node, context.xml_attr.name, value)
