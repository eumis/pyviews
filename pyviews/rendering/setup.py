'''Used for node setup'''

class NodeSetup:
    '''Contains data, logic used for render steps'''
    def __init__(self, render_steps=None, get_child_args=None):
        self.render_steps = render_steps
        self.get_child_args = get_child_args

    def get_child_init_args(self, node, **args):
        '''Returns init arguments for children nodes'''
        args = {}
        if self.get_child_args:
            args = self.get_child_args(node)
        return args if args else {}
