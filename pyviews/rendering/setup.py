'''Used for node setup'''

from typing import List
from pyviews.core.node import SETTER

class NodeSetup:
    '''Contains node setters, render steps, e.t.c'''
    def __init__(self, setters: List[SETTER] = None, render_steps=None, get_child_init_args=None):
        self._setters = setters
        self._render_steps = render_steps
        self._get_child_init_args = get_child_init_args

    @property
    def setters(self):
        '''Returns property setters'''
        return self._setters

    @property
    def render_steps(self):
        '''Returns render steps'''
        return self._render_steps

    def get_child_init_args(self, node):
        '''Returns init arguments for children nodes'''
        args = {}
        if self._get_child_init_args:
            args = self._get_child_init_args(node)
        return args if args else {}
