'''Defaul dependencies for pyviews.core'''

from pyviews.core.ioc import register_single, register_func
from pyviews.rendering.node import create_node
from pyviews.rendering.pipeline import RenderingPipeline
from pyviews.rendering.pipeline import render, render_children, apply_attributes
from pyviews.rendering.binding import BindingFactory

def register_defaults():
    '''Registers defaults dependencies'''
    register_func('create_node', create_node)
    register_func('render', render)
    register_single('binding_factory', BindingFactory())
    register_single('pipeline', create_default_pipeline())

def create_default_pipeline() -> RenderingPipeline:
    '''Creates default node setup'''
    return RenderingPipeline(steps=[
        apply_attributes,
        render_children
    ])
