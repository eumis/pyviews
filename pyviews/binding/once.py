"""Once binding"""

from pyviews.binding.binder import BindingContext
from pyviews.core.expression import execute


def run_once(context: BindingContext):
    """Calls setter with expression value"""
    value = execute(context.expression_body, context.node.node_globals)
    context.setter(context.node, context.xml_attr.name, value)
