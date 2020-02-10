from functools import partial
from unittest.mock import Mock, call

from pytest import fixture, mark

from pyviews.binding import BindingContext
from pyviews.binding.expression import ExpressionBinding, bind_to_expression
from pyviews.binding.tests.common import SomeEntity, InnerViewModel, ParentViewModel
from pyviews.compilation import Expression
from pyviews.core import InheritedDict, XmlAttr


@fixture
def expression_binding_fixture(request):
    inner_vm = InnerViewModel(2, 'inner str')
    view_model = ParentViewModel(3, inner_vm)
    expression = Expression(
        'str(vm.int_value) + vm.inner_vm.str_value + vm.get_val() + vm.inner_vm.get_val()')
    target_inst = SomeEntity()
    callback = partial(setattr, target_inst, 'str_value')
    binding = ExpressionBinding(callback, expression, InheritedDict({'vm': view_model}))
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
