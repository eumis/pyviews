"""Classes used for binding"""

from abc import ABC, abstractmethod
from typing import Callable, Any

from .error import ViewsError


class BindingError(ViewsError):
    """Base error for binding errors"""
    TargetUpdateError = 'Error occurred during target update'


BindingCallback = Callable[[Any], None]


class Binding(ABC):
    """Binds BindingTarget to changes"""

    def __init__(self):
        self.add_error_info = lambda error: None

    @abstractmethod
    def bind(self):
        """Applies binding"""

    @abstractmethod
    def destroy(self):
        """Destroys binding"""
