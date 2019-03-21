'''Code expressions abstractions'''

from abc import ABC, abstractmethod
from typing import List
from .common import CoreError

class CompilationError(CoreError):
    '''Error for failed expression compilation'''
    def __init__(self, message, expression):
        super().__init__(message)
        self.expression = expression
        self.add_info('Expression', expression)

class ObjectNode:
    '''Entry of object in expression'''
    def __init__(self, key):
        self.key = key
        self.children: List['ObjectNode'] = []

class Expression(ABC):
    '''Code expression.'''
    @abstractmethod
    def get_object_tree(self) -> ObjectNode:
        '''Returns objects tree root from expression'''

    @abstractmethod
    def execute(self, parameters: dict = None) -> any:
        '''Executes expression with passed parameters and returns result'''
