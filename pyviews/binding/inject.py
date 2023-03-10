from injectool import resolve

from pyviews.binding.binder import BindingContext
from pyviews.core.expression import execute


def inject_binding(context: BindingContext):
    """Calls setter with expression value"""
    resolve_key = execute(context.expression_body, context.node.node_globals)
    value = resolve(resolve_key)
    context.setter(context.node, context.xml_attr.name, value)
