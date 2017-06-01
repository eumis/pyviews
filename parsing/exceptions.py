class BindingException(Exception):
    pass

class CommandException(Exception):
    pass

class InstanceException(Exception):
    pass

class UnsupportedNodeException(Exception):
    def __init__(self, type):
        Exception.__init__(self, type + ' type element should be of type view.base.CompileNode')
    