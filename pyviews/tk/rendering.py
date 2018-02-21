'''Customizing of tk parsing'''

from tkinter import Entry, StringVar
from tkinter.ttk import Widget as TtkWidget
from pyviews.core.xml import XmlAttr
from pyviews.core.node import NodeArgs
from pyviews.core.compilation import Expression
from pyviews.core.binding import InstanceTarget, PropertyExpressionTarget
from pyviews.core.binding import ExpressionBinding, TwoWaysBinding
from pyviews.rendering.core import apply_attribute, parse_expression
from pyviews.rendering.binding import BindingArgs
from pyviews.tk.binding import VariableBinding
from pyviews.tk.widgets import WidgetNode
from pyviews.tk.ttk import TtkWidgetNode

def convert_to_node(inst, args: NodeArgs):
    '''Wraps instance with WidgetNode'''
    args = (inst, args['xml_node'], args['parent_context'])
    if isinstance(inst, TtkWidget):
        return TtkWidgetNode(*args)
    return WidgetNode(*args)

def apply_text(node: WidgetNode):
    '''Applies xml node content to WidgetNode'''
    if not node.xml_node.text:
        return
    text_attr = XmlAttr('text', node.xml_node.text)
    apply_attribute(node, text_attr)

def is_entry_twoways(args: BindingArgs):
    '''suitable for entry two ways binding'''
    try:
        return isinstance(args.node.widget, Entry)
    except AttributeError:
        return False

def apply_entry_twoways(args: BindingArgs):
    '''
    Applies "twoways" binding.
    Expression result is assigned to property.
    Property is set on expression change.
    Wrapped instance is changed on property change
    '''
    (var_key, expr_body) = parse_expression(args.expr_body)
    var = args.node.globals[var_key]() \
                if args.node.globals.has_key(var_key) else StringVar
    args.node.widget.config(textvariable=var)
    args.node.define_setter('text', lambda node, value: var.set(value))

    expression = Expression(expr_body)
    target = InstanceTarget(args.node, args.attr.name, args.modifier)
    expr_binding = ExpressionBinding(target, expression, args.node.globals)

    target = PropertyExpressionTarget(expression, args.node.globals)
    obs_binding = VariableBinding(target, var)

    two_ways_binding = TwoWaysBinding(expr_binding, obs_binding)
    two_ways_binding.bind()
    args.node.add_binding(two_ways_binding)
