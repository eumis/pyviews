class ViewModel:
    def __init__(self):
        public_keys = [(key, getattr(self, key)) for key in dir(self) if _is_public(key)]
        self._callbacks = {key: [] for (key, value) in public_keys if callable(value)}

    def observe(self, prop, callback):
        if prop in self._callbacks:
            self._callbacks[prop].append(callback)

    def release_callback(self, prop, callback):
        if prop in self._callbacks:
            if callback in self._callbacks[prop]:
                self._callbacks[prop].remove(callback)

    def get_observable_keys(self):
        return self._callbacks.keys()

    def __setattr__(self, name, new_val):
        old_val = self.__dict__[name] if name in self.__dict__ else None
        self.__dict__[name] = new_val
        if not _is_public(name):
            return
        if name not in self._callbacks:
            self._callbacks[name] = []
        else:
            self._notify(name, new_val, old_val)

    def _notify(self, prop, new_val, old_val):
        if new_val == old_val or prop not in self._callbacks:
            return
        for callback in self._callbacks[prop]:
            callback(new_val, old_val)

def _is_public(key: str):
    return not key.startswith('_')

class Dictionary(dict):
    def __init__(self, parent=None):
        super().__init__()
        self._parent = parent
        self._callbacks = []

    def observe(self, callback):
        self._callbacks.append(callback)

    def __len__(self):
        keys = set(self.keys())
        if self._parent is not None:
            keys.update(self._parent.keys())
        return len(keys)

    def __getitem__(self, key):
        if key in self:
            return dict.__getitem__(self, key)
        if self._parent is not None:
            return self._parent[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        old_value = self._try_get_value(key)
        dict.__setitem__(self, key, value)
        for callback in self._callbacks:
            callback(value, old_value)

    def _try_get_value(self, key):
        value = None
        try:
            value = self[key]
        except KeyError:
            pass
        return value
