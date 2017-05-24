class ViewModel:
    def __init__(self):
        self.callbacks = {}

    def notify(self, property, newValue, oldValue):
        if self.callbacks[property] is None or newValue == oldValue:
            return
        for callback in self.callbacks[property]:
            callback(newValue, oldValue)

    def observe(self, property, callback):
        if self.callbacks[property] is None:
            self.callbacks[property] = []
        self.callbacks[property].append(callback)
