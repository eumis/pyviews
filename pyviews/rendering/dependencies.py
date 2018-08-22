'''Defaul dependencies for pyviews.core'''

from pyviews.core.ioc import register_single, register_func
from pyviews.rendering.core import render_old, apply_attributes, render_children
from pyviews.rendering.core import create_node_old, apply_code
from pyviews.rendering.node import convert_to_node
from pyviews.rendering.binding import BindingFactory
from pyviews.rendering.node import Code

def register_defaults():
    '''Registers defaults dependencies'''
    register_func('create_node', create_node_old)
    register_func('convert_to_node', convert_to_node)
    register_func('render', render_old)
    register_func('set_attr', setattr)
    register_single('rendering_steps', [apply_attributes, render_children])
    register_single('rendering_steps', [apply_code, render_children], Code)
    register_single('binding_factory', BindingFactory())
