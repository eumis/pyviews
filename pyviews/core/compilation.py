"""Code expressions abstractions"""

from abc import ABC, abstractmethod
from typing import List

from injectool import resolve

from .error import CoreError


class CompilationError(CoreError):
    """Error for failed expression compilation"""

    def __init__(self, message, expr: 'Expression'):
        super().__init__(message)
        self.expression: Expression = expr
        self.add_info('Expression', expression)


class ObjectNode:
    """Entry of object in expression"""

    def __init__(self, key):
        self.key = key
        self.children: List['ObjectNode'] = []


class Expression(ABC):
    """Code expression."""

    def __init__(self, code):
        self._code: str = code

    @property
    def code(self) -> str:
        """Expression source code"""
        return self._code

    @abstractmethod
    def get_object_tree(self) -> ObjectNode:
        """Returns objects tree root from expression"""

    @abstractmethod
    def execute(self, parameters: dict = None) -> any:
        """Executes expression with passed parameters and returns result"""


def expression(code: str) -> Expression:
    """Creates Expression instance"""
    return resolve(Expression)(code)
