'''Defaul dependencies for pyviews.core'''

from pyviews.core.ioc import register_single, register_func
from pyviews.core.node import Node, InstanceNode
from pyviews.rendering.node import create_node
from pyviews.rendering.flow import render, render_children, apply_attributes
from pyviews.rendering.binding import BindingFactory
from pyviews.rendering.setup import NodeSetup

def register_defaults():
    '''Registers defaults dependencies'''
    register_func('create_node', create_node)
    register_func('render', render)
    register_single('binding_factory', BindingFactory())
    register_single('node_setup', create_default_node_setup(setattr))
    register_single('node_setup', create_default_node_setup(_instance_node_setter), InstanceNode)

def create_default_node_setup(setter):
    '''Creates default node setup'''
    node_setup = NodeSetup()
    node_setup.render_steps = [
        apply_attributes,
        render_children
    ]
    node_setup.setter = setter
    node_setup.get_child_args = _init_args_getter
    return node_setup

def _init_args_getter(node: Node):
    return {'parent_node': node}

def _instance_node_setter(node: InstanceNode, key: str, value):
    inst_to_set = node.instance
    if hasattr(node, key):
        inst_to_set = node
    setattr(inst_to_set, key, value)
