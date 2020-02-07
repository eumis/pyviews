from functools import partial
from typing import Callable
from unittest.mock import Mock

from pytest import fixture, mark

from pyviews.binding import BindingContext, InlineBinding
from pyviews.binding.inline import bind_inline
from pyviews.compilation import Expression
from pyviews.core import ObservableEntity, InheritedDict, XmlAttr


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
