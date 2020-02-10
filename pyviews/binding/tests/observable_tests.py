from functools import partial

from pytest import fixture, mark

from pyviews.binding.observable import ObservableBinding
from pyviews.binding.tests.common import InnerViewModel


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
