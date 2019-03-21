'''Classes used for binding'''

from abc import ABC, abstractmethod
from .common import CoreError

class BindingError(CoreError):
    '''Base error for binding errors'''
    TargetUpdateError = 'Error occured during target update'

class BindingTarget(ABC):
    '''Target for changes, applied when binding has triggered changes'''
    @abstractmethod
    def on_change(self, value):
        '''Called to apply changes'''

class Binding(ABC):
    '''Binds BindingTarget to changes'''
    def __init__(self):
        self.add_error_info = lambda error: None

    @abstractmethod
    def bind(self):
        '''Applies binding'''

    @abstractmethod
    def destroy(self):
        '''Destroys binding'''

class BindingRule(ABC):
    '''Creates binding for args'''
    @abstractmethod
    def suitable(self, **args) -> bool:
        '''Returns True if rule is suitable for args'''

    @abstractmethod
    def apply(self, **args):
        '''Applies binding'''

class Binder:
    '''Applies binding'''
    def __init__(self):
        self._rules = {}

    def add_rule(self, binding_type: str, rule: BindingRule):
        '''Adds new rule'''
        if binding_type not in self._rules:
            self._rules[binding_type] = []

        self._rules[binding_type].insert(0, rule)

    def find_rule(self, binding_type: str, **args):
        '''Finds rule by binding type and args'''
        try:
            rules = self._rules[binding_type]
            return next(rule for rule in rules if rule.suitable(**args))
        except (KeyError, StopIteration):
            return None

    def apply(self, binding_type, **args):
        '''Returns apply function'''
        rule = self.find_rule(binding_type, **args)
        if rule is None:
            error = BindingError('Binding rule is not found')
            error.add_info('Binding type', binding_type)
            error.add_info('args', args)
            raise error
        binding = rule.apply(**args)
        if binding:
            args['node'].add_binding(rule.apply(**args))
