from pyviews.core import ObservableEntity


class InnerViewModel(ObservableEntity):
    def __init__(self, int_value, str_value):
        super().__init__()
        self._val = ''
        self.int_value = int_value
        self.str_value = str_value
        self._add_key('get_val')

    def set_val(self, value):
        old_val = self._val
        self._val = value
        self._notify('get_val', value, old_val)

    def get_val(self):
        return self._val


class ParentViewModel(ObservableEntity):
    def __init__(self, int_value, inner_vm):
        super().__init__()
        self._val = ''
        self.int_value = int_value
        self.inner_vm = inner_vm
        self.another_vm = inner_vm
        self._add_key('get_val')

    def set_val(self, value):
        old_val = self._val
        self._val = value
        self._notify('get_val', value, old_val)

    def get_val(self):
        return self._val


class SomeEntity:
    def __init__(self):
        self.int_value = 1
        self.str_value = 'str'
