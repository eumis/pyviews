'''Used for node setup'''

from typing import List
from pyviews.core.node import SETTER, Node

class NodeSetup:
    '''Contains node setters, render steps, e.t.c'''
    def __init__(self, setter=None, render_steps=None, get_child_init_args=None):
        self._setter = setter
        self._render_steps = render_steps
        self._get_child_init_args = get_child_init_args

    @property
    def render_steps(self) -> List:
        '''Returns render steps'''
        return self._render_steps

    def get_child_init_args(self, node):
        '''Returns init arguments for children nodes'''
        args = {}
        if self._get_child_init_args:
            args = self._get_child_init_args(node)
        return args if args else {}

    def apply(self, node: Node):
        '''Applies setup to passed node'''
        node.setter = self._setter
