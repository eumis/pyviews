from functools import partial

from pytest import fixture, mark

from pyviews.binding.observable import ObservableBinding
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


@fixture
def observable_binding_fixture(request):
    target_inst = InnerViewModel(1, '1')
    callback = partial(setattr, target_inst, 'int_value')

    inst = InnerViewModel(5, '1')
    binding = ObservableBinding(callback, inst, 'int_value')
    binding.bind()

    request.cls.inst = inst
    request.cls.target_inst = target_inst
    request.cls.binding = binding


@mark.usefixtures('observable_binding_fixture')
class ObservableBindingTests:
    """ObservableBinding tests"""

    def test_initialize_target(self):
        """Target should be updated with property value on Binding.bind() call"""
        assert self.inst.int_value == self.target_inst.int_value

    def test_binding(self):
        """Target should be updated after expression result is changed"""
        new_val = self.target_inst.int_value + 1

        self.inst.int_value = new_val

        assert self.target_inst.int_value == new_val

    def test_destroy(self):
        """Destroy should stop handling observable changes and update target"""
        old_value = self.target_inst.int_value

        self.binding.destroy()
        self.inst.int_value = self.inst.int_value + 2

        assert self.target_inst.int_value == old_value
