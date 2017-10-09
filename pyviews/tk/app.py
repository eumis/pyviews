from os.path import abspath
from pyviews.core import ioc
from pyviews.core.parsing import parse_attributes, parse_children
from pyviews.tk.parsing import convert_to_node
from pyviews.tk.views import parse_view
from pyviews.tk.geometry import apply_geometry
from pyviews.tk.modifiers import set_attr

def register_dependencies():
    ioc.register_value('convert_to_node', convert_to_node)
    ioc.register_value('views_folder', abspath('views'))
    ioc.register_value('view_ext', '.xml')
    ioc.register_value('parsing_steps', [parse_attributes, apply_geometry, parse_children])
    ioc.register_value('set_attr', set_attr)

def launch(root_view=None):
    root_view = 'root' if root_view is None else root_view
    root = parse_view(root_view)
    root.widget.mainloop()
