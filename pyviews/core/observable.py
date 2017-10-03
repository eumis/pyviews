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
        if key in self._callbacks:
            for callback in self._callbacks[key].copy():
                callback(value, old_value)

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
        if key not in self.__dict__:
            raise KeyError('Entity ' + str(self) + 'doesn''t have attribute' + key)
        super().observe(key, callback)

# class ObservableDict(Observable, dict):
#     def __init__(self):
#         super().__init__()
#         self._callbacks = set()

#     def __setitem__(self, key, value):
#         old_value = self._try_get_value(key)
#         dict.__setitem__(self, key, value)
#         for callback in self._callbacks:
#             callback(key, value, old_value)

#     def _try_get_value(self, key):
#         value = None
#         try:
#             value = self[key]
#         except KeyError:
#             pass
#         return value

#     def observe(self, callback):
#         self._callbacks.add(callback)

#     def release(self, callback):
#         try:
#             self._callbacks.remove(callback)
#         except KeyError:
#             pass
