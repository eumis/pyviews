"""Classes used for binding"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from pyviews.core.error import PyViewsError, ViewInfo


class BindingError(PyViewsError):
    """Base error for binding errors"""

    def __init__(self, message: Optional[str] = None, view_info: Optional[ViewInfo] = None):
        super().__init__(message = message, view_info = view_info)


BindingCallback = Callable[[Any], None]


class Binding(ABC):
    """Binds BindingTarget to changes"""

    @abstractmethod
    def bind(self):
        """Applies binding"""

    @abstractmethod
    def destroy(self):
        """Destroys binding"""
