'''Package for creation instances from xml and its values to expressions'''

from os import linesep

class CoreError(Exception):
    '''Base error class for custom exceptions'''
    def __init__(self, message, inner_message=None):
        self.msg = message if inner_message is None else message + linesep + '\t' + inner_message
        super().__init__(self.msg)
