from functools import partial

from pytest import fixture, mark

from pyviews.binding import ExpressionBinding, ObservableBinding
from pyviews.binding.binding import get_update_property_expression
from pyviews.binding.twoways import TwoWaysBinding
from pyviews.compilation import Expression
from pyviews.core import InheritedDict, ObservableEntity


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


@fixture
def two_ways_fixture(request):
    observable_inst = InnerViewModel(1, '1')
    expr_inst = InnerViewModel(1, '1')

    expr_globals = InheritedDict({'vm': expr_inst})
    expression = Expression('vm.int_value')

    on_update = partial(setattr, observable_inst, 'int_value')
    one_binding = ExpressionBinding(on_update, expression, expr_globals)

    expr_target = get_update_property_expression(expression, expr_globals)
    two_binding = ObservableBinding(expr_target, observable_inst, 'int_value')

    binding = TwoWaysBinding(one_binding, two_binding)
    binding.bind()

    request.cls.observable_inst = observable_inst
    request.cls.expr_inst = expr_inst
    request.cls.binding = binding


@mark.usefixtures('two_ways_fixture')
class TwoWaysBindingTests:
    """TwoWaysBinding tests using ExpressionBinding and ObservableBinding"""

    def test_expression_binding(self):
        """Observable property should be bound to expression"""
        new_value = self.expr_inst.int_value + 5

        self.expr_inst.int_value = new_value

        assert self.observable_inst.int_value == new_value

    def test_observable_binding(self):
        """Property from expression should be bound to observable property"""
        new_value = self.observable_inst.int_value + 5

        self.observable_inst.int_value = new_value

        assert self.expr_inst.int_value == new_value

    def test_expression_binding_destroy(self):
        """Expression binding should be destroyed"""
        self.binding.destroy()
        old_value = self.observable_inst.int_value
        new_expr_value = old_value + 5

        self.expr_inst.int_value = new_expr_value

        assert self.observable_inst.int_value == old_value

    def test_observable_binding_destroy(self):
        """Observable binding should be destroyed"""
        self.binding.destroy()
        old_value = self.expr_inst.int_value
        new_observable_value = old_value + 5

        self.observable_inst.int_value = new_observable_value

        assert self.expr_inst.int_value == old_value
