from unittest.mock import Mock, call

from pytest import fixture, mark

from pyviews.binding import BindingContext
from pyviews.binding.expression import ExpressionBinding, bind_setter_to_expression
from pyviews.binding.tests.common import InnerViewModel, ParentViewModel
from pyviews.expression import Expression, execute
from pyviews.core import InheritedDict, XmlAttr


@fixture
def expression_binding_fixture(request):
    inner_vm = InnerViewModel(0, 'inner str')
    view_model = ParentViewModel(0, inner_vm)
    expression = Expression(
        'str(vm.int_value + vm.int_value)'
        ' + vm.inner_vm.str_value + vm.inner_vm.str_value'
        ' + vm.get_val() + vm.inner_vm.get_val()')
    callback, global_vars = Mock(), InheritedDict({'vm': view_model})
    binding = ExpressionBinding(callback, expression, global_vars)
    binding.bind()

    request.cls.expression = expression
    request.cls.view_model = view_model
    request.cls.callback = callback
    request.cls.binding = binding
    request.cls.global_vars = global_vars


@mark.usefixtures('expression_binding_fixture')
class ExpressionBindingTests:
    """ExpressionBinding tests"""

    def test_initialize_target(self):
        """Target should be updated with expression value on Binding.bind() call"""
        expected = execute(self.expression, self.global_vars.to_dictionary())

        assert self.callback.call_args_list == [call(expected)]

    @mark.parametrize('change', [
        lambda gl: setattr(gl['vm'], 'int_value', 3),
        lambda gl: setattr(gl['vm'].inner_vm, 'str_value', 'new str value'),
        lambda gl: setattr(gl['vm'], 'inner_vm', InnerViewModel(50, 'new inner value')),
        lambda gl: setattr(gl['vm'].inner_vm, 'str_value', 'new str value'),
        lambda gl: gl['vm'].set_val('asdf'),
        lambda gl: gl['vm'].inner_vm.set_val('asdf')
    ])
    def test_expression_changed(self, change):
        """Target should be updated after expression result is changed"""
        change(self.global_vars)
        expected = execute(self.expression, self.global_vars.to_dictionary())

        assert self.callback.call_args_list[1:] == [call(expected)]

    def test_destroy(self):
        """Destroy should stop handling expression changes and update target"""
        self.callback.reset_mock()
        self.binding.destroy()
        self.view_model.int_value = self.view_model.int_value + 1
        self.view_model.inner_vm.str_value = self.view_model.inner_vm.str_value + "changes"

        assert not self.callback.called


@fixture
def binding_context_fixture(request):
    setter, xml_attr = Mock(), XmlAttr('name')
    context = BindingContext({
        'setter': setter,
        'xml_attr': xml_attr,
        'expression_body': '1+1',
        'node': Mock(node_globals=InheritedDict())
    })

    request.cls.context = context


@mark.usefixtures('binding_context_fixture')
class BindSetterToExpressionTests:
    def test_binds_setter_to_expression_changes(self):
        """should bind setter to expression changes"""
        self.context.node = Mock(node_globals=InheritedDict({'value': 1}))
        self.context.expression_body = 'value'

        bind_setter_to_expression(self.context)
        self.context.setter.reset_mock()
        self.context.node.node_globals['value'] = 2

        assert self.context.setter.call_args == call(self.context.node, self.context.xml_attr.name, 2)

    def test_returns_binding(self):
        """should return expression binding"""
        actual = bind_setter_to_expression(self.context)

        assert isinstance(actual, ExpressionBinding)
