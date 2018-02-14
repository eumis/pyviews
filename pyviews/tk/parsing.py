'''Customizing of tk parsing'''

from tkinter import Entry, StringVar
from tkinter.ttk import Widget as TtkWidget
from pyviews.core.xml import XmlAttr
from pyviews.core.node import NodeArgs
from pyviews.core.compilation import Expression
from pyviews.core.binding import InstanceTarget, ExpressionBinding, TwoWaysBinding, PropertyExpressionTarget
from pyviews.core.parsing import parse_attr, BindingFactory, parse_expression
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

class TkBindingFactory(BindingFactory):
    def get_apply(self, binding_type, node, attr, modifier):
        if hasattr(node, 'widget') and isinstance(node.widget, Entry) and binding_type == 'twoways':
            return apply_entry_twoways
        return super().get_apply(binding_type, node, attr, modifier)

def apply_entry_twoways(expr_body, node: WidgetNode, attr, modifier):
    '''
    Applies "twoways" binding.
    Expression result is assigned to property.
    Property is set on expression change.
    Wrapped instance is changed on property change
    '''
    (converter_key, expr_body) = parse_expression(expr_body)
    var = StringVar()
    node.widget.config(textvariable=var)
    node.define_setter('text', lambda node, value: var.set(str(value)))

    expression = Expression(expr_body)
    target = InstanceTarget(node, attr.name, modifier)
    expr_binding = ExpressionBinding(target, expression, node.globals)

    target = PropertyExpressionTarget(expression, node.globals)
    converter = node.globals[converter_key] if node.globals.has_key(converter_key) else None
    obs_binding = VariableBinding(target, var, converter)

    two_ways_binding = TwoWaysBinding(expr_binding, obs_binding)
    two_ways_binding.bind()
    node.add_binding(two_ways_binding)
