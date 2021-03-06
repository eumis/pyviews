from unittest.mock import Mock

from pytest import fixture, mark, raises

from pyviews.binding.tests.common import InnerViewModel, ParentViewModel
from pyviews.binding.twoways import TwoWaysBinding, get_expression_callback
from pyviews.core import InheritedDict, BindingError
from pyviews.expression import Expression, execute


@fixture
def two_ways_fixture(request):
    one, two = Mock(), Mock()
    binding = TwoWaysBinding(one, two)

    request.cls.one = one
    request.cls.two = two
    request.cls.binding = binding


@mark.usefixtures('two_ways_fixture')
class TwoWaysBindingTests:
    """TwoWaysBinding tests using ExpressionBinding and ObservableBinding"""

    def test_bind(self):
        """should bind both bindings"""
        self.binding.bind()

        assert self.one.bind.called and self.two.bind.called

    def test_destroy(self):
        """should bind both bindings"""
        self.binding.destroy()

        assert self.one.destroy.called and self.two.destroy.called


class GetPropertyExpressionCallbackTests:
    """get_property_expression_callback() tests"""

    @staticmethod
    @mark.parametrize('expression', ['', '[vm, 2]', 'vm.int_value + val'])
    def test_raises(expression):
        """Should raise BindingError if expression is not property expression"""
        with raises(BindingError):
            get_expression_callback(Expression(expression), InheritedDict())

    @staticmethod
    @mark.parametrize('expression_body, value, globals_dict', [
        ('vm.int_value', 10, {'vm': ParentViewModel(0, InnerViewModel(0, ''))}),
        ('vm.inner_vm.int_value', 134, {'vm': ParentViewModel(0, InnerViewModel(0, ''))}),
        ('vm.inner_vm.str_value', 'value', {'vm': ParentViewModel(0, InnerViewModel(0, ''))}),
        ('vm.inner_vm', InnerViewModel(50, 'a'), {'vm': ParentViewModel(0, InnerViewModel(0, ''))})
    ])
    def test_callback_updates_property(expression_body, value, globals_dict):
        """returned callback should update target property"""
        expression, global_vars = Expression(expression_body), InheritedDict(globals_dict)
        callback = get_expression_callback(expression, global_vars)

        callback(value)

        assert execute(expression, global_vars.to_dictionary()) == value

    @staticmethod
    @mark.parametrize('key, value', [
        ('int_value', 10),
        ('vm', InnerViewModel(50, 'a')),
        ('str_value', 'some value')
    ])
    def test_callback_updates_global_value(key, value):
        """returned callback should update target property"""
        global_vars = InheritedDict({key: None})
        callback = get_expression_callback(Expression(key), global_vars)

        callback(value)

        assert global_vars[key] == value
