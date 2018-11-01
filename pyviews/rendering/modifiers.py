'''Module with modifiers'''

from pyviews.core.ioc import get_current_scope
from pyviews.core.reflection import import_path
from pyviews.core.node import Node

def import_global(node: Node, key, path):
    '''Import passed module, class, function full name and stores it to node's globals'''
    node.node_globals[key] = import_path(path)

def inject_global(node: Node, global_key, inject_key):
    '''Resolves passed dependency and stores it to node's globals'''
    value = get_current_scope().container.get(inject_key)
    set_global(node, global_key, value)

def set_global(node: Node, key, value):
    '''Adds passed value to node's globals'''
    node.node_globals[key] = value

def call(node, key, value):
    '''Empty modifier used to run expression for node'''
    pass
