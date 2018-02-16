'''tkinter application entry point'''

from os.path import abspath
from pyviews.core import ioc
from pyviews.rendering.dependencies import register_defaults
from pyviews.rendering.core import parse_attributes, parse_children
from pyviews.rendering.binding import BindingFactory
from pyviews.tk.rendering import convert_to_node, apply_text, is_entry_twoways, apply_entry_twoways
from pyviews.tk.views import parse_view
from pyviews.tk.modifiers import set_attr
from pyviews.tk.styles import Style, parse_attrs as parse_style_attrs, apply_styles
from pyviews.tk.geometry import Row, Column, apply_layout
from pyviews.tk.widgets import Root
from pyviews.tk.ttk import Style as TtkStyle, apply_ttk_style
from pyviews.tk import canvas

def register_dependencies():
    '''Registers all dependencies needed for application'''
    register_defaults()
    ioc.register_value('convert_to_node', convert_to_node)
    ioc.register_value('views_folder', abspath('views'))
    ioc.register_value('view_ext', '.xml')
    ioc.register_value('set_attr', set_attr)
    ioc.register_value('styles', {})
    ioc.register_value('apply_styles', apply_styles)
    _register_binding_factory()
    _register_parsing_steps()

def _register_binding_factory():
    factory = BindingFactory()
    factory.add_rule('twoways', BindingFactory.Rule(is_entry_twoways, apply_entry_twoways))
    ioc.register_value('binding_factory', factory)

def _register_parsing_steps():
    ioc.register_value('parsing_steps', [parse_attributes, apply_text, parse_children])
    ioc.register_value('parsing_steps', [parse_attributes, parse_children], Root)
    ioc.register_value('parsing_steps', [parse_style_attrs, parse_children], Style)
    ioc.register_value('parsing_steps',
                       [parse_attributes, apply_ttk_style, parse_children],
                       TtkStyle)
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
    '''Runs application. Widgets are created from passed xml_files'''
    root_view = 'root' if root_view is None else root_view
    root = parse_view(root_view)
    root.widget.mainloop()
