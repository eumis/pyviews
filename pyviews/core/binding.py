"""Classes used for binding"""

from abc import ABC, abstractmethod
from typing import Callable, Any

from .error import PyViewsError


class BindingError(PyViewsError):
    """Base error for binding errors"""

    def __init__(self, message: str = None):
        super().__init__(message=message)


BindingCallback = Callable[[Any], None]


class Binding(ABC):
    """Binds BindingTarget to changes"""

    @abstractmethod
    def bind(self):
        """Applies binding"""

    @abstractmethod
    def destroy(self):
        """Destroys binding"""
