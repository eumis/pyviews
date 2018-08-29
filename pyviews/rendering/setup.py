'''Used for node setup'''

from pyviews.core.node import Node

class NodeSetup:
    '''Contains node setters, render steps, e.t.c'''
    def __init__(self, setter=None, render_steps=None, child_init_args_getter=None, properties=None):
        self.setter = setter
        self.render_steps = render_steps
        self.child_init_args_getter = child_init_args_getter
        self.properties = properties

    def get_child_init_args(self, node, **args):
        '''Returns init arguments for children nodes'''
        args = {}
        if self.child_init_args_getter:
            args = self.child_init_args_getter(node)
        return args if args else {}

    def apply(self, node: Node):
        '''Applies setup to passed node'''
        if self.setter:
            node.setter = self.setter
        if self.properties:
            node.properties = {key: prop.new(node) for key, prop in self.properties.items()}
