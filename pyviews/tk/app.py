from os.path import abspath
from pyviews.core import ioc
from pyviews.core.parsing import parse_attributes, parse_children
from pyviews.tk.parsing import convert_to_node, apply_text
from pyviews.tk.views import parse_view
from pyviews.tk.modifiers import set_attr
from pyviews.tk.styles import Style, apply_styles
from pyviews.tk.geometry import Row, Column, apply_layout
from pyviews.tk.widgets import Root

def register_dependencies():
    ioc.register_value('convert_to_node', convert_to_node)
    ioc.register_value('views_folder', abspath('views'))
    ioc.register_value('view_ext', '.xml')
    ioc.register_value('set_attr', set_attr)
    _register_parsing_steps()

def _register_parsing_steps():
    ioc.register_value('parsing_steps', [parse_attributes, apply_text, parse_children])
    ioc.register_value('parsing_steps', [parse_attributes, parse_children], Root)
    ioc.register_value('parsing_steps', [apply_styles], Style)
    ioc.register_value('parsing_steps', [apply_layout], Row)
    ioc.register_value('parsing_steps', [apply_layout], Column)

def launch(root_view=None):
    root_view = 'root' if root_view is None else root_view
    root = parse_view(root_view)
    root.widget.mainloop()
