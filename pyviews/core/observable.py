'''Observable implementations'''

class Observable:
    '''Base class for observable entities'''
    def __init__(self):
        self._callbacks = {}
        self._all_callbacks = []

    def observe(self, key, callback):
        '''Subscribes to key changes'''
        if key not in self._callbacks:
            self._add_key(key)
        self._callbacks[key].append(callback)

    def _add_key(self, key):
        self._callbacks[key] = []

    def observe_all(self, callback):
        '''Subscribes to all keys changes'''
        self._all_callbacks.append(callback)

    def _notify(self, key, value, old_val):
        self._notify_prop(key, value, old_val)
        self._notify_all(key, value, old_val)

    def _notify_prop(self, key, value, old_value):
        if value == old_value:
            return
        try:
            for callback in self._callbacks[key].copy():
                callback(value, old_value)
        except KeyError:
            pass

    def _notify_all(self, key, value, old_value):
        if self._all_callbacks is None:
            self._all_callbacks = []
        for callback in self._all_callbacks.copy():
            callback(key, value, old_value)

    def release(self, key, callback):
        '''Releases callback from key changes'''
        try:
            self._callbacks[key].remove(callback)
        except (KeyError, ValueError):
            pass

    def release_all(self, callback):
        '''Releases callback from all keys changes'''
        self._all_callbacks.remove(callback)

class ObservableEntity(Observable):
    '''Observable general object'''
    def __init__(self):
        super().__setattr__('_callbacks', {})
        super().__setattr__('_all_callbacks', [])

    def __setattr__(self, key, value):
        old_val = getattr(self, key) if key in self.__dict__ else None
        super().__setattr__(key, value)
        self._notify(key, value, old_val)

    def observe(self, key, callback):
        '''Subscribes to key changes'''
        if key not in self.__dict__ and key not in self._callbacks:
            raise KeyError('Entity ' + str(self) + 'doesn''t have attribute' + key)
        super().observe(key, callback)

class InheritedDict(Observable):
    '''Dictionary that pulls value from parent if doesn't have own'''
    def __init__(self, parent=None):
        super().__init__()
        self._container = parent.to_dictionary() if parent else {}
        self._parent = parent
        if self._parent:
            self._parent.observe_all(self._parent_changed)
        self._own_keys = set()

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

    def _parent_changed(self, key, value, old_value):
        if key in self._own_keys:
            return
        self._set_value(key, value, old_value)

    def to_dictionary(self):
        '''Returns all values as dict'''
        return self._container.copy()

    def has_key(self, key):
        '''Checks key presence in hierarchy'''
        return key in self._container

    def remove_key(self, key):
        '''Remove own key, value'''
        try:
            self._own_keys.discard(key)
            if self._parent and self._parent.has_key(key):
                self._container[key] = self._parent[key]
            else:
                del self._container[key]
        except KeyError:
            pass

    def get(self, key, default=None):
        '''Retuns value by value. default is return in case key does not exist'''
        try:
            return self[key]
        except KeyError:
            return default
            