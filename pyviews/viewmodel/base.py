class ViewModel:
    def __init__(self):
        public_keys = [(key, getattr(self, key)) for key in dir(self) if is_public(key)]
        self._callbacks = {key: [] for (key, value) in public_keys if callable(value)}

    def notify(self, prop, new_val, old_val):
        if new_val == old_val or prop not in self._callbacks:
            return
        for callback in self._callbacks[prop]:
            callback(new_val, old_val)

    def observe(self, prop, callback):
        if prop in self._callbacks:
            self._callbacks[prop].append(callback)

    def get_observable_keys(self):
        return self._callbacks.keys()

    def __setattr__(self, name, new_val):
        old_val = self.__dict__[name] if name in self.__dict__ else None
        self.__dict__[name] = new_val
        if not is_public(name):
            return
        if name not in self._callbacks:
            self._callbacks[name] = []
        else:
            self.notify(name, new_val, old_val)

def is_public(key):
    return not key.startswith('_')
