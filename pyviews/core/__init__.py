'''Package for creation instances from xml and its values to expressions'''

from os import linesep

class CoreError(Exception):
    '''Base error class for custom exceptions'''
    def __init__(self, message, inner_message=None):
        self.msg = message if inner_message is None else message + linesep + '\t' + inner_message
        super().__init__(self.msg)

def get_not_implemented_message(instance, method):
    '''returns error message for NotImplementedError'''
    return 'Method "{0}" is not defind in {1}'.format(method, instance.__class__.__name__)
