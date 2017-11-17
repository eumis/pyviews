class Observable:
    def __init__(self):
        self._callbacks = {}

    def observe(self, key, callback):
        if key not in self._callbacks:
            self._callbacks[key] = []
        self._callbacks[key].append(callback)

    def _notify(self, key, value, old_value):
        if value == old_value:
            return
        try:
            for callback in self._callbacks[key].copy():
                callback(value, old_value)
        except KeyError:
            pass

    def release(self, key, callback):
        try:
            self._callbacks[key].remove(callback)
        except KeyError:
            pass

class ObservableEnt(Observable):
    def __setattr__(self, key, value):
        old_val = getattr(self, key) if key in self.__dict__ else None
        super().__setattr__(key, value)
        self._notify(key, value, old_val)

    def observe(self, key, callback):
        if key not in self.__dict__ and key not in self._callbacks:
            raise KeyError('Entity ' + str(self) + 'doesn''t have attribute' + key)
        super().observe(key, callback)
