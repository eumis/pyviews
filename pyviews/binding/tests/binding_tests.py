from unittest.mock import Mock, call

from pytest import fixture, mark, raises

from pyviews.binding import BindingContext
from pyviews.binding.binding import get_update_global_value, get_update_property_expression, \
    run_once
from pyviews.compilation import Expression
from pyviews.core import ObservableEntity, InheritedDict, BindingError, XmlAttr


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
