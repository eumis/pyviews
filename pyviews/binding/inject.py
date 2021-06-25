from injectool import resolve

from pyviews.binding import BindingContext
from pyviews.expression import execute


def inject_binding(context: BindingContext):
    """Calls setter with expression value"""
    resolve_key = execute(context.expression_body, context.node.node_globals.to_dictionary())
    value = resolve(resolve_key)
    context.setter(context.node, context.xml_attr.name, value)
