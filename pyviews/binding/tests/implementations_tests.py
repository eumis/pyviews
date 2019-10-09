from pytest import fixture, mark, raises

from pyviews.core import ObservableEntity, InheritedDict, BindingError
from pyviews.compilation import CompiledExpression
from pyviews.binding.implementations import PropertyTarget, FunctionTarget
from pyviews.binding.implementations import PropertyExpressionTarget, GlobalValueExpressionTarget
from pyviews.binding.implementations import ExpressionBinding, ObservableBinding, TwoWaysBinding


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


@fixture(name='target_entity')
def target_entity_fixture():
    return SomeEntity(), 25


def test_property_target(target_entity):
    """"PropertyTarget.on_change test"""
    inst, new_val = target_entity
    target = PropertyTarget(inst, 'int_value', setattr)

    target.on_change(new_val)

    assert inst.int_value == new_val


def test_function_target(target_entity):
    """"FunctionTarget.on_change test"""
    inst, new_val = target_entity
    target = FunctionTarget(lambda value: setattr(inst, 'int_value', value))

    target.on_change(new_val)

    assert inst.int_value == new_val


@fixture
def expression_binding_fixture(request):
    inner_vm = InnerViewModel(2, 'inner str')
    view_model = ParentViewModel(3, inner_vm)
    expression = CompiledExpression(
        'str(vm.int_value) + vm.inner_vm.str_value + vm.get_val() + vm.inner_vm.get_val()')
    target_inst = SomeEntity()
    target = PropertyTarget(target_inst, 'str_value', setattr)
    binding = ExpressionBinding(target, expression, InheritedDict({'vm': view_model}))
    binding.bind()

    request.cls.expression = expression
    request.cls.view_model = view_model
    request.cls.target_inst = target_inst
    request.cls.binding = binding


@mark.usefixtures('expression_binding_fixture')
class ExpressionBindingTests:
    """ExpressionBinding tests"""

    def test_initialize_target(self):
        """Target should be updated with expression value on Binding.bind() call"""
        expected = self.expression.execute({'vm': self.view_model})

        assert self.target_inst.str_value == expected

    @mark.parametrize('change', [
        lambda vm: setattr(vm, 'int_value', 3),
        lambda vm: setattr(vm.inner_vm, 'str_value', 'new str value'),
        lambda vm: setattr(vm, 'inner_vm', InnerViewModel(50, 'new inner value')),
        lambda vm: setattr(vm.inner_vm, 'str_value', 'new str value'),
        lambda vm: vm.set_val('asdf'),
        lambda vm: vm.inner_vm.set_val('asdf'),
    ])
    def test_expression_changed(self, change):
        """Target should be updated after expression result is changed"""
        change(self.view_model)
        expected = self.expression.execute({'vm': self.view_model})

        assert self.target_inst.str_value == expected

    def test_destroy(self):
        """Destroy should stop handling expression changes and update target"""
        old_value = self.target_inst.str_value

        self.binding.destroy()
        self.view_model.int_value = self.view_model.int_value + 1
        self.view_model.inner_vm.str_value = self.view_model.inner_vm.str_value + "changes"

        actual = self.target_inst.str_value

        assert actual == old_value


@fixture(params=[
    ('vm.int_value', False),
    ('vm.inner_vm.int_value', True)
])
def expression_target_fixture(request):
    code, is_inner = request.param

    inner = InnerViewModel(1, '1')
    parent = ParentViewModel(1, inner)
    expression = CompiledExpression(code)
    expr_globals = InheritedDict({'vm': parent})

    request.cls.target = PropertyExpressionTarget(expression, expr_globals)
    request.cls.target_vm = inner if is_inner else parent


@mark.usefixtures('expression_target_fixture')
class PropertyExpressionTargetTests:
    """PropertyExpressionTarget tests"""

    @staticmethod
    @mark.parametrize('expression', ['vm', 'vm.int_value + val'])
    def test_raises(expression):
        """Should raise BindingError if expression is not property expression"""
        with raises(BindingError):
            PropertyExpressionTarget(CompiledExpression(expression), InheritedDict())

    def test_change(self):
        """PropertyExpressionTarget.on_change should update target property"""
        new_val = self.target_vm.int_value + 5

        self.target.on_change(new_val)

        assert self.target_vm.int_value == new_val


@fixture
def expr_globals_fixture(request):
    request.cls.expr_globals = InheritedDict({'one': 1})


@mark.usefixtures('expr_globals_fixture')
class GlobalValueExpressionTargetTests:
    """GlobalValueExpressionTarget tests"""

    @mark.parametrize('expression', [
        'vm.int_value',
        'vm + val'
    ])
    def test_raises(self, expression):
        """Should raise BindingError for invalid expression"""
        with raises(BindingError):
            GlobalValueExpressionTarget(CompiledExpression(expression), self.expr_globals)

    def test_change(self):
        """GlobalValueExpressionTarget.on_change should update target property"""
        target = GlobalValueExpressionTarget(CompiledExpression("vm"), self.expr_globals)
        new_val = 25

        target.on_change(new_val)

        assert self.expr_globals['vm'] == new_val


@fixture
def observable_binding_fixture(request):
    target_inst = InnerViewModel(1, '1')
    expr_globals = InheritedDict({'vm': target_inst})
    expression = CompiledExpression('vm.int_value')
    target = PropertyExpressionTarget(expression, expr_globals)

    inst = InnerViewModel(5, '1')

    binding = ObservableBinding(target, inst, 'int_value')
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


@fixture
def two_ways_fixture(request):
    observable_inst = InnerViewModel(1, '1')
    expr_inst = InnerViewModel(1, '1')

    expr_globals = InheritedDict({'vm': expr_inst})
    expression = CompiledExpression('vm.int_value')

    observable_target = PropertyTarget(observable_inst, 'int_value', setattr)
    one_binding = ExpressionBinding(observable_target, expression, expr_globals)

    expr_target = PropertyExpressionTarget(expression, expr_globals)
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
