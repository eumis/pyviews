from functools import partial
from unittest.mock import Mock

from pytest import fixture, mark

from pyviews.binding import BindingContext, InlineBinding
from pyviews.binding.inline import bind_inline
from pyviews.binding.tests.common import InnerViewModel
from pyviews.expression import Expression
from pyviews.core import InheritedDict, XmlAttr, BindingCallback


@fixture
def inline_binding_fixture(request):
    target_instance = InnerViewModel(0, '0')
    source_instance = InnerViewModel(1, '1')
    request.cls.binding_callback = None
    destroy = Mock()

    def bind(binding_callback: BindingCallback):
        request.cls.binding_callback = binding_callback

        return destroy

    expr_globals = InheritedDict({'vm': source_instance, 'bind': bind})
    bind_expression = Expression('bind')
    value_expression = Expression('vm.int_value')

    callback = partial(setattr, target_instance, 'int_value')
    binding = InlineBinding(callback, bind_expression, value_expression, expr_globals)
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
        self.binding_callback()

        assert self.target_instance.int_value == self.source_instance.int_value

    def test_bind_calls_bind_function_from_bind_expression(self):
        """bind() method calls bind function returned from bind_expression with binding_callback function"""
        assert self.binding_callback is not None

    def test_binding_callback_updates_target(self):
        """binding_callback() passed by binding should evaluate value_expression and update target with it"""
        self.source_instance.int_value = 2

        self.binding_callback()

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
        'setter': Mock(),
        'xml_attr': XmlAttr('name')
    })

    actual = bind_inline(context)

    assert isinstance(actual, InlineBinding)
