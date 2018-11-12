'''Defaul dependencies for pyviews.core'''

from pyviews.core.ioc import register_single, register_func
from pyviews.rendering.node import create_node
from pyviews.rendering.pipeline import RenderingPipeline
from pyviews.rendering.pipeline import render_node, render_children, apply_attributes
from pyviews.rendering.binding import BindingFactory
from pyviews.code import Code, get_code_setup

def register_defaults():
    '''Registers defaults dependencies'''
    register_func('create_node', create_node)
    register_func('render', render_node)
    register_single('binding_factory', BindingFactory())
    register_single('pipeline', create_default_pipeline())
    register_single('pipeline', get_code_setup(), Code)

def create_default_pipeline() -> RenderingPipeline:
    '''Creates default node setup'''
    return RenderingPipeline(steps=[
        apply_attributes,
        lambda node, **args: render_children(node, node_globals=node.node_globals)
    ])
