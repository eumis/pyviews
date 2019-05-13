"""Classes used for binding"""

from abc import ABC, abstractmethod
from .error import CoreError


class BindingError(CoreError):
    """Base error for binding errors"""
    TargetUpdateError = 'Error occurred during target update'


class BindingTarget(ABC):
    """Target for changes, applied when binding has triggered changes"""

    @abstractmethod
    def on_change(self, value):
        """Called to apply changes"""


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


class BindingRule(ABC):
    """Creates binding for args"""

    @abstractmethod
    def suitable(self, **args) -> bool:
        """Returns True if rule is suitable for args"""

    @abstractmethod
    def apply(self, **args):
        """Applies binding"""


