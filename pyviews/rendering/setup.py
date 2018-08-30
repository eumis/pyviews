'''Used for node setup'''

from pyviews.core.node import Node

class NodeSetup:
    '''Contains node setters, render steps, e.t.c'''
    def __init__(self, **args):
        self.setter = args.get('setter')
        self.render_steps = args.get('render_steps', None)
        self.get_child_args = args.get('get_child_args')
        self.properties = args.get('properties')
        self.on_destroy = args.get('on_destroy')

    def get_child_init_args(self, node, **args):
        '''Returns init arguments for children nodes'''
        args = {}
        if self.get_child_args:
            args = self.get_child_args(node)
        return args if args else {}

    def apply(self, node: Node):
        '''Applies setup to passed node'''
        if self.setter:
            node.setter = self.setter

        if self.properties:
            node.properties = {key: prop.new(node) for key, prop in self.properties.items()}

        if self.on_destroy:
            node.on_destroy = self.on_destroy
