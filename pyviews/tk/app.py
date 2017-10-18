from os.path import abspath
from inspect import getmembers, isclass
from pyviews.core import ioc
from pyviews.core.parsing import parse_attributes, parse_children
from pyviews.tk.parsing import convert_to_node, apply_text
from pyviews.tk.views import parse_view
from pyviews.tk.modifiers import set_attr
from pyviews.tk import widgets

def register_dependencies():
    ioc.register_value('convert_to_node', convert_to_node)
    ioc.register_value('views_folder', abspath('views'))
    ioc.register_value('view_ext', '.xml')
    ioc.register_value('set_attr', set_attr)
    _register_parsing_steps()

def _register_parsing_steps():
    is_widget_node = lambda member: isclass(member) \
                     and (issubclass(member, widgets.WidgetNode) or member == widgets.WidgetNode)
    steps = [parse_attributes, apply_text, parse_children]
    for name, widget_node_type in getmembers(widgets, is_widget_node):
        ioc.register_value('parsing_steps', steps, widget_node_type)
    ioc.register_value('parsing_steps', [parse_attributes, parse_children], widgets.Root)

def launch(root_view=None):
    root_view = 'root' if root_view is None else root_view
    root = parse_view(root_view)
    root.widget.mainloop()
