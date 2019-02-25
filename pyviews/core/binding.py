'''Classes used for binding'''

from .common import CoreError, get_not_implemented_message

class BindingError(CoreError):
    '''Base error for binding errors'''
    TargetUpdateError = 'Error occured during target update'

class BindingTarget:
    '''Target for changes, applied when binding has triggered changes'''
    def on_change(self, value):
        '''Called to apply changes'''
        raise NotImplementedError(get_not_implemented_message(self, 'on_change'))

class Binding:
    '''Binds BindingTarget to changes'''
    def __init__(self):
        self.add_error_info = lambda error: None

    def bind(self):
        '''Applies binding'''
        raise NotImplementedError(get_not_implemented_message(self, 'bind'))

    def destroy(self):
        '''Destroys binding'''
        raise NotImplementedError(get_not_implemented_message(self, 'destroy'))
