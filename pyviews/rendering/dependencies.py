'''Defaul dependencies for pyviews.core'''

from pyviews.core.ioc import register_single, register_func
from pyviews.rendering.core import parse, parse_attributes, parse_children, convert_to_node
from pyviews.rendering.binding import BindingFactory

def register_defaults():
    '''Registers defaults dependencies'''
    register_func('convert_to_node', convert_to_node)
    register_func('parse', parse)
    register_func('set_attr', setattr)
    register_single('parsing_steps', [parse_attributes, parse_children])
    register_single('binding_factory', BindingFactory())
