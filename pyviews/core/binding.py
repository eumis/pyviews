"""Classes used for binding"""

from abc import ABC, abstractmethod
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Callable, Generator, Optional, Set, Union

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


@dataclass
class BindableRecord:
    bindable: 'Bindable'
    key: str

    def __eq__(self, other: 'BindableRecord'):
        return self.bindable is other.bindable and self.key == other.key

    def __hash__(self):
        return hash((id(self.bindable), self.key))


_CONTEXT_VAR: ContextVar[Set[BindableRecord]] = ContextVar('recording')


@contextmanager
def recording() -> Generator[Set[BindableRecord], None, None]:
    """Stores rendering context to context var"""
    records_set = set()
    token = _CONTEXT_VAR.set(records_set)
    try:
        yield records_set
    finally:
        _CONTEXT_VAR.reset(token)


class Bindable:
    """Base class for observable entities"""

    def __init__(self):
        self._callbacks = {}

    def __getattribute__(self, name: str):
        bindable_recording = _CONTEXT_VAR.get(None)
        if bindable_recording is not None and not name.startswith('_'):
            bindable_recording.add(BindableRecord(self, name))
        return super().__getattribute__(name)

    def observe(self, key: str, callback: Callable[[Any, Any], None]):
        """Subscribes to key changes"""
        if key not in self._callbacks:
            self._add_key(key)
        self._callbacks[key].append(callback)

    def _add_key(self, key):
        self._callbacks[key] = []

    def _notify(self, key: str, value, old_value):
        if value == old_value:
            return
        try:
            for callback in self._callbacks[key].copy():
                callback(value, old_value)
        except KeyError:
            pass

    def release(self, key: str, callback: Callable[[Any, Any], None]):
        """Releases callback from key changes"""
        try:
            self._callbacks[key] = [c for c in self._callbacks[key] if c != callback]
        except (KeyError, ValueError):
            pass


class BindableEntity(Bindable):
    """Bindable general object"""

    def __setattr__(self, key, value):
        if key in self.__dict__:
            old_val = getattr(self, key, None)
            Bindable.__setattr__(self, key, value)
            self._notify(key, value, old_val)
        else:
            Bindable.__setattr__(self, key, value)

    def observe(self, key, callback: Callable[[Any, Any], None]):
        """Subscribes to key changes"""
        if key not in self.__dict__ and key not in self._callbacks:
            raise KeyError('Entity ' + str(self) + "doesn't have attribute" + key)
        super().observe(key, callback)


class BindableDict(dict, Bindable):

    def __init__(self, source: Optional[Union[dict, 'BindableDict']] = None):
        if source is not None:
            dict.__init__(self, source)
        else:
            dict.__init__(self)
        Bindable.__init__(self)
        self._all_callbacks = []

    def __getattribute__(self, name: str):
        return object.__getattribute__(self, name)

    def __getitem__(self, key: Any):
        bindable_recording = _CONTEXT_VAR.get(None)
        if bindable_recording is not None:
            bindable_recording.add(BindableRecord(self, key))
        return dict.__getitem__(self, key)

    def __setitem__(self, key: Any, value: Any):
        try:
            old_value = self[key]
        except KeyError:
            old_value = None
        dict.__setitem__(self, key, value)
        self._notify(key, value, old_value)

    def __delitem__(self, key: Any):
        value = self[key]
        super().__delitem__(key)
        self._notify(key, None, value)

    def get(self, key: Any, default: Any = None) -> Any:
        bindable_recording = _CONTEXT_VAR.get(None)
        if bindable_recording is not None:
            bindable_recording.add(BindableRecord(self, key))
        return super().get(key, default)

    def pop(self, key: Any, default: Any = None) -> None:
        if key in self:
            value = super().pop(key)
            self._notify(key, None, value)
        else:
            value = default
        return value

    def observe_all(self, callback: Callable[[str, Any, Any], None]):
        """Subscribes to all keys changes"""
        self._all_callbacks.append(callback)

    def _notify(self, key: str, value: Any, old_value: Any):
        super()._notify(key, value, old_value)
        self._notify_all(key, value, old_value)

    def _notify_all(self, key: str, value, old_value):
        if self._all_callbacks is None:
            self._all_callbacks = []
        for callback in self._all_callbacks.copy():
            callback(key, value, old_value)

    def release_all(self, callback: Callable[[str, Any, Any], None]):
        """Releases callback from all keys changes"""
        self._all_callbacks = [c for c in self._all_callbacks if c != callback]
