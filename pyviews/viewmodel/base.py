class ViewModel:
    def __init__(self):
        self.callbacks = {}

    def notify(self, prop, new_val, old_val):
        if prop not in self.callbacks or new_val == old_val:
            return
        for callback in self.callbacks[prop]:
            callback(new_val, old_val)

    def observe(self, prop, callback):
        if not hasattr(self, prop):
            return
        if prop not in self.callbacks:
            self.callbacks[prop] = []
        self.callbacks[prop].append(callback)
