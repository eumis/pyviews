"""Observable implementations"""

from typing import Callable, Any, Union


class Observable:
    """Base class for observable entities"""

    def __init__(self):
        self._callbacks = {}

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


class ObservableEntity(Observable):
    """Observable general object"""

    def __setattr__(self, key, value):
        if key in self.__dict__:
            old_val = getattr(self, key, None)
            Observable.__setattr__(self, key, value)
            self._notify(key, value, old_val)
        else:
            Observable.__setattr__(self, key, value)

    def observe(self, key, callback: Callable[[Any, Any], None]):
        """Subscribes to key changes"""
        if key not in self.__dict__ and key not in self._callbacks:
            raise KeyError('Entity ' + str(self) + "doesn't have attribute" + key)
        super().observe(key, callback)


class InheritedDict(Observable):
    """Dictionary that pulls value from parent if doesn't have own"""

    def __init__(self, source: Union[dict, 'InheritedDict'] = None):
        super().__init__()
        self._parent = None
        self._container = {}
        self._own_keys = set()
        self._all_callbacks = []

        if isinstance(source, InheritedDict):
            self.inherit(source)
        elif source:
            self._container = source.copy()
            self._own_keys = set(self._container.keys())

    def __getitem__(self, key):
        return self._container[key]

    def __setitem__(self, key, value):
        try:
            old_value = self[key]
            self._own_keys.add(key)
        except KeyError:
            old_value = None
        self._set_value(key, value, old_value)

    def _set_value(self, key, value, old_value):
        self._container[key] = value
        self._notify(key, value, old_value)

    def __len__(self):
        return len(self._container)

    def __contains__(self, item):
        return item in self._container

    def inherit(self, parent: 'InheritedDict'):
        """Inherit passed dictionary"""
        if self._parent == parent:
            return
        if self._parent:
            self._parent.release_all(self._parent_changed)
        self_values = {key: self._container[key] for key in self._own_keys}
        self._container = {**parent.to_dictionary(), **self_values}
        self._parent = parent
        self._parent.observe_all(self._parent_changed)

    def _parent_changed(self, key, value, old_value):
        if key in self._own_keys:
            return
        self._set_value(key, value, old_value)

    def observe_all(self, callback: Callable[[str, Any, Any], None]):
        """Subscribes to all keys changes"""
        self._all_callbacks.append(callback)

    def _notify(self, key: str, value, old_value):
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

    def to_dictionary(self) -> dict:
        """Returns all values as dict"""
        return self._container.copy()

    def remove_key(self, key):
        """Remove own key, value"""
        try:
            self._own_keys.discard(key)
            if self._parent and key in self._parent:
                self._container[key] = self._parent[key]
            else:
                del self._container[key]
        except KeyError:
            pass

    def get(self, key, default=None):
        """Returns value by value. default is return in case key does not exist"""
        try:
            return self[key]
        except KeyError:
            return default
