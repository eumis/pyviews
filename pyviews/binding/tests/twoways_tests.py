from functools import partial

from pytest import fixture, mark, raises

from pyviews.binding import ExpressionBinding, ObservableBinding
from pyviews.binding.twoways import TwoWaysBinding, get_property_expression_callback, get_global_value_callback
from pyviews.compilation import Expression
from pyviews.core import InheritedDict, ObservableEntity, BindingError


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

    expr_target = get_property_expression_callback(expression, expr_globals)
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


@fixture(params=[
    ('vm.int_value', False),
    ('vm.inner_vm.int_value', True)
])
def expression_target_fixture(request):
    code, is_inner = request.param

    inner = InnerViewModel(1, '1')
    parent = ParentViewModel(1, inner)
    expression = Expression(code)
    expr_globals = InheritedDict({'vm': parent})

    request.cls.binding_callback = get_property_expression_callback(expression, expr_globals)
    request.cls.target_vm = inner if is_inner else parent


@mark.usefixtures('expression_target_fixture')
class GetPropertyExpressionCallbackTests:
    """get_property_expression_callback() tests"""

    @staticmethod
    @mark.parametrize('expression', ['vm', 'vm.int_value + val'])
    def test_raises(expression):
        """Should raise BindingError if expression is not property expression"""
        with raises(BindingError):
            get_property_expression_callback(Expression(expression), InheritedDict())

    def test_change(self):
        """PropertyExpressionTarget.on_change should update target property"""
        new_val = self.target_vm.int_value + 5

        self.binding_callback(new_val)

        assert self.target_vm.int_value == new_val


@fixture
def expr_globals_fixture(request):
    request.cls.expr_globals = InheritedDict({'one': 1})


@mark.usefixtures('expr_globals_fixture')
class GetGlobalValueCallbackTests:
    """get_global_value_callback() tests"""

    @mark.parametrize('expression', [
        'vm.int_value',
        'vm + val'
    ])
    def test_raises(self, expression):
        """Should raise BindingError for invalid expression"""
        with raises(BindingError):
            get_global_value_callback(Expression(expression), self.expr_globals)

    def test_change(self):
        """GlobalValueExpressionTarget.on_change should update target property"""
        callback = get_global_value_callback(Expression("vm"), self.expr_globals)
        new_val = 25

        callback(new_val)

        assert self.expr_globals['vm'] == new_val
