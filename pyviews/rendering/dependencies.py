'''Defaul dependencies for pyviews.core'''

from pyviews.core.ioc import register_value
from pyviews.rendering.core import parse, parse_attributes, parse_children, convert_to_node
from pyviews.rendering.binding import BindingFactory

def register_defaults():
    '''Registers defaults dependencies'''
    register_value('convert_to_node', convert_to_node)
    register_value('parse', parse)
    register_value('parsing_steps', [parse_attributes, parse_children])
    register_value('set_attr', setattr)
    register_value('binding_factory', BindingFactory())
