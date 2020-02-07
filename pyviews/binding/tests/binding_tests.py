from functools import partial
from typing import Callable
from unittest.mock import Mock, call

from pytest import fixture, mark, raises

from pyviews.binding import BindingContext
from pyviews.core import ObservableEntity, InheritedDict, BindingError, XmlAttr
from pyviews.compilation import Expression
from pyviews.binding.binding import InlineBinding, get_update_global_value, get_update_property_expression, \
    bind_to_expression, bind_inline, run_once
from pyviews.binding.binding import ExpressionBinding, ObservableBinding, TwoWaysBinding


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

    # def test_property_target(target_entity):
    #     """"PropertyTarget.on_change test"""
    #     inst, new_val = target_entity
    #     target = PropertyTarget(inst, 'int_value', setattr)
    #
    #     target.on_change(new_val)
    #
    #     assert inst.int_value == new_val

    # def test_function_target(target_entity):
    #     """"FunctionTarget.on_change test"""
    #     inst, new_val = target_entity
    #     target = FunctionTarget(lambda value: setattr(inst, 'int_value', value))
    #
    #     target.on_change(new_val)
    #
    #     assert inst.int_value == new_val


@mark.parametrize('expr_body, node_globals, expected_value', [
    ('1+1', {}, 2),
    ('val', {'val': 2}, 2),
    ('val + 1', {'val': 2}, 3)
])
def test_run_once(expr_body: str, node_globals: dict, expected_value):
    """run_once() should call passed modifier"""
    node = Mock(node_globals=InheritedDict(node_globals))
    modifier, xml_attr = Mock(), XmlAttr('name')

    run_once(BindingContext({
        'node': node,
        'expression_body': expr_body,
        'modifier': modifier,
        'xml_attr': xml_attr
    }))

    assert modifier.call_args == call(node, xml_attr.name, expected_value)


@fixture
def expression_binding_fixture(request):
    inner_vm = InnerViewModel(2, 'inner str')
    view_model = ParentViewModel(3, inner_vm)
    expression = Expression(
        'str(vm.int_value) + vm.inner_vm.str_value + vm.get_val() + vm.inner_vm.get_val()')
    target_inst = SomeEntity()
    on_update = partial(setattr, target_inst, 'str_value')
    binding = ExpressionBinding(on_update, expression, InheritedDict({'vm': view_model}))
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


@fixture
def binding_context_fixture(request):
    modifier, xml_attr = Mock(), XmlAttr('name')
    context = BindingContext({
        'modifier': modifier,
        'xml_attr': xml_attr,
        'expression_body': '1+1',
        'node': Mock(node_globals=InheritedDict())
    })

    request.cls.context = context


@mark.usefixtures('binding_context_fixture')
class BindToExpressionTests:
    def test_binds_modifier_to_expression_changes(self):
        """should bind modifier to expression changes"""
        self.context.node = Mock(node_globals=InheritedDict({'value': 1}))
        self.context.expression_body = 'value'

        bind_to_expression(self.context)
        self.context.modifier.reset_mock()
        self.context.node.node_globals['value'] = 2

        assert self.context.modifier.call_args == call(self.context.node, self.context.xml_attr.name, 2)

    def test_returns_binding(self):
        """should return expression binding"""
        actual = bind_to_expression(self.context)

        assert isinstance(actual, ExpressionBinding)


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

    request.cls.on_update = get_update_property_expression(expression, expr_globals)
    request.cls.target_vm = inner if is_inner else parent


@mark.usefixtures('expression_target_fixture')
class GetUpdatePropertyExpressionTests:
    """PropertyExpressionTarget tests"""

    @staticmethod
    @mark.parametrize('expression', ['vm', 'vm.int_value + val'])
    def test_raises(expression):
        """Should raise BindingError if expression is not property expression"""
        with raises(BindingError):
            get_update_property_expression(Expression(expression), InheritedDict())

    def test_change(self):
        """PropertyExpressionTarget.on_change should update target property"""
        new_val = self.target_vm.int_value + 5

        self.on_update(new_val)

        assert self.target_vm.int_value == new_val


@fixture
def expr_globals_fixture(request):
    request.cls.expr_globals = InheritedDict({'one': 1})


@mark.usefixtures('expr_globals_fixture')
class GetUpdateGlobalValueTests:
    """GlobalValueExpressionTarget tests"""

    @mark.parametrize('expression', [
        'vm.int_value',
        'vm + val'
    ])
    def test_raises(self, expression):
        """Should raise BindingError for invalid expression"""
        with raises(BindingError):
            get_update_global_value(Expression(expression), self.expr_globals)

    def test_change(self):
        """GlobalValueExpressionTarget.on_change should update target property"""
        on_update = get_update_global_value(Expression("vm"), self.expr_globals)
        new_val = 25

        on_update(new_val)

        assert self.expr_globals['vm'] == new_val


@fixture
def observable_binding_fixture(request):
    target_inst = InnerViewModel(1, '1')
    on_update = partial(setattr, target_inst, 'int_value')

    inst = InnerViewModel(5, '1')
    binding = ObservableBinding(on_update, inst, 'int_value')
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


@fixture
def inline_binding_fixture(request):
    target_instance = InnerViewModel(0, '0')
    source_instance = InnerViewModel(1, '1')
    request.cls.update_target = None
    destroy = Mock()

    def bind(update_target: Callable[[], None]):
        request.cls.update_target = update_target

        return destroy

    expr_globals = InheritedDict({'vm': source_instance, 'bind': bind})
    bind_expression = Expression('bind')
    value_expression = Expression('vm.int_value')

    on_update = partial(setattr, target_instance, 'int_value')
    binding = InlineBinding(on_update, bind_expression, value_expression, expr_globals)
    binding.bind()

    request.cls.target_instance = target_instance
    request.cls.source_instance = source_instance
    request.cls.binding = binding
    request.cls.destroy = destroy


@mark.usefixtures('inline_binding_fixture')
class InlineBindingTests:
    """InlineBinding class tests"""

    def test_updates_target_on_binding(self):
        """bind() should update target with value expression result"""
        self.update_target()

        assert self.target_instance.int_value == self.source_instance.int_value

    def test_bind_calls_bind_function_from_bind_expression(self):
        """bind() method calls bind function returned from bind_expression with update_target() function"""
        assert self.update_target is not None

    def test_update_target_updates_target(self):
        """update_target() passed by binding should evaluate value_expression and update target with it"""
        self.source_instance.int_value = 2

        self.update_target()

        assert self.target_instance.int_value == self.source_instance.int_value

    def test_destroy_called(self):
        """destroy() should call function returned as bind result"""
        self.binding.destroy()

        assert self.destroy.called


def test_bind_inline():
    bind = Mock()
    context = BindingContext({
        'node': Mock(node_globals=InheritedDict({
            'bind': bind,
            'value': 1
        })),
        'expression_body': 'bind()}:{value',
        'modifier': Mock(),
        'xml_attr': XmlAttr('name')
    })

    actual = bind_inline(context)

    assert isinstance(actual, InlineBinding)
