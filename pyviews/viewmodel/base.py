class ViewModel:
    def __init__(self):
        self._callbacks = {}

    def notify(self, prop, new_val, old_val):
        if prop not in self._callbacks or new_val == old_val:
            return
        for callback in self._callbacks[prop]:
            callback(new_val, old_val)

    def observe(self, prop, callback):
        if prop in self._callbacks:
            self._callbacks[prop].append(callback)

    def define_prop(self, key, default=None):
        self._callbacks[key] = []
        self.__dict__[key] = default

    def __setattr__(self, name, new_val):
        old_val = self.__dict__[name] if name in self.__dict__ else None
        self.__dict__[name] = new_val
        self.notify(name, new_val, old_val)
