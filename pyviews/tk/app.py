from os.path import abspath
from pyviews.core import ioc
from pyviews.core.parsing import parse_attributes, parse_children
from pyviews.tk.parsing import convert_to_node, apply_text
from pyviews.tk.views import parse_view
from pyviews.tk.modifiers import set_attr
from pyviews.tk.styles import Style, parse_attrs as parse_style_attrs, init_styles
from pyviews.tk.geometry import Row, Column, apply_layout
from pyviews.tk.widgets import Root
from pyviews.tk import canvas

def register_dependencies():
    ioc.register_value('convert_to_node', convert_to_node)
    ioc.register_value('views_folder', abspath('views'))
    ioc.register_value('view_ext', '.xml')
    ioc.register_value('set_attr', set_attr)
    _register_parsing_steps()

def _register_parsing_steps():
    ioc.register_value('parsing_steps', [parse_attributes, apply_text, parse_children])
    ioc.register_value('parsing_steps', [init_styles, parse_attributes, parse_children], Root)
    ioc.register_value('parsing_steps', [parse_style_attrs], Style)
    ioc.register_value('parsing_steps', [apply_layout], Row)
    ioc.register_value('parsing_steps', [apply_layout], Column)
    _register_canvas_parsing_steps()

def _register_canvas_parsing_steps():
    ioc.register_value('parsing_steps', [parse_attributes, canvas.render], canvas.Arc)
    ioc.register_value('parsing_steps', [parse_attributes, canvas.render], canvas.Bitmap)
    ioc.register_value('parsing_steps', [parse_attributes, canvas.render], canvas.Image)
    ioc.register_value('parsing_steps', [parse_attributes, canvas.render], canvas.Line)
    ioc.register_value('parsing_steps', [parse_attributes, canvas.render], canvas.Oval)
    ioc.register_value('parsing_steps', [parse_attributes, canvas.render], canvas.Polygon)
    ioc.register_value('parsing_steps', [parse_attributes, canvas.render], canvas.Rectangle)
    ioc.register_value('parsing_steps', [parse_attributes, canvas.render], canvas.Text)
    ioc.register_value('parsing_steps', [parse_attributes, canvas.render], canvas.Window)

def launch(root_view=None):
    root_view = 'root' if root_view is None else root_view
    root = parse_view(root_view)
    root.widget.mainloop()
