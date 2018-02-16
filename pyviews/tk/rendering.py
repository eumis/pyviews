'''Customizing of tk parsing'''

from tkinter import Entry, StringVar
from tkinter.ttk import Widget as TtkWidget
from pyviews.core.xml import XmlAttr
from pyviews.core.node import NodeArgs
from pyviews.core.compilation import Expression
from pyviews.core.binding import InstanceTarget, PropertyExpressionTarget
from pyviews.core.binding import ExpressionBinding, TwoWaysBinding
from pyviews.rendering.core import parse_attr, parse_expression
from pyviews.rendering.binding import BindingFactory
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
    parse_attr(node, text_attr)

def is_entry_twoways(args: BindingFactory.Args):
    '''suitable for entry two ways binding'''
    try:
        return isinstance(args.node.widget, Entry)
    except AttributeError:
        return False

def apply_entry_twoways(args: BindingFactory.Args):
    '''
    Applies "twoways" binding.
    Expression result is assigned to property.
    Property is set on expression change.
    Wrapped instance is changed on property change
    '''
    (converter_key, expr_body) = parse_expression(args.expr_body)
    var = StringVar()
    args.node.widget.config(textvariable=var)
    args.node.define_setter('text', lambda node, value: var.set(str(value)))

    expression = Expression(expr_body)
    target = InstanceTarget(args.node, args.attr.name, args.modifier)
    expr_binding = ExpressionBinding(target, expression, args.node.globals)

    target = PropertyExpressionTarget(expression, args.node.globals)
    converter = args.node.globals[converter_key] \
                if args.node.globals.has_key(converter_key) else None
    obs_binding = VariableBinding(target, var, converter)

    two_ways_binding = TwoWaysBinding(expr_binding, obs_binding)
    two_ways_binding.bind()
    args.node.add_binding(two_ways_binding)
