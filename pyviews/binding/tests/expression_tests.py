from unittest.mock import Mock, call

from pytest import fixture, mark

from pyviews.binding.binder import BindingContext
from pyviews.binding.expression import ExpressionBinding, bind_setter_to_expression, get_expression_callback
from pyviews.binding.tests.common import InnerViewModel, ParentViewModel
from pyviews.core.bindable import BindableDict
from pyviews.core.expression import Expression, execute
from pyviews.core.rendering import NodeGlobals
from pyviews.core.xml import XmlAttr


@fixture
def expression_binding_fixture(request):
    inner_vm = InnerViewModel(0, 'inner str')
    view_model = ParentViewModel(0, inner_vm)
    callback = Mock()

    request.cls.view_model = view_model
    request.cls.callback = callback


@mark.usefixtures('expression_binding_fixture')
class ExpressionBindingTests:
    """ExpressionBinding tests"""

    callback: Mock

    def _bind(self, expression: Expression, global_vars: NodeGlobals) -> ExpressionBinding:
        binding = ExpressionBinding(self.callback, expression, global_vars)
        binding.bind()

        return binding

    @mark.parametrize('source, global_dict', [
        ('vm', {'vm': InnerViewModel(0, '')}),
        ('vm.int_value', {'vm': InnerViewModel(2, '')}),
        ('vm.str_value', {'vm': InnerViewModel(2, 'asdf')}),
        ('(vm.int_value, parent.inner_vm.int_value)', {
            'vm': InnerViewModel(2, 'asdf'),
            'parent': ParentViewModel(0, InnerViewModel(0, ''))
        }),
    ]) # yapf: disable
    def test_initialize_target(self, source: str, global_dict: dict):
        """Target should be updated with expression value on Binding.bind() call"""
        expression = Expression(source)

        self._bind(expression, NodeGlobals(global_dict))

        expected = execute(expression, global_dict)
        assert self.callback.call_args == call(expected)

    @mark.parametrize('source, global_dict, change', [
        ('vm.int_value', {'vm': InnerViewModel(0, '')},
         lambda gl: setattr(gl['vm'], 'int_value', 3)),
        ('vm.inner_vm.int_value', {'vm': ParentViewModel(0, InnerViewModel(0, ''))},
         lambda gl: setattr(gl['vm'], 'inner_vm', InnerViewModel(5, 'updated'))),
        ('vm.inner_vm.str_value', {'vm': ParentViewModel(0, InnerViewModel(0, ''))},
         lambda gl: setattr(gl['vm'].inner_vm, 'str_value', 'asdf')
         ),
        ('(vm.int_value, parent.inner_vm.int_value)',
         {'vm': InnerViewModel(0, ''),
          'parent': ParentViewModel(0, InnerViewModel(0, ''))},
         lambda gl: setattr(gl['parent'].inner_vm, 'int_value', 3)
         ),
        ('(vm.str_value, str(parent.inner_vm.int_value))',
         {'vm': InnerViewModel(0, ''),
          'parent': ParentViewModel(0, InnerViewModel(0, ''))},
         lambda gl: setattr(gl['parent'].inner_vm, 'int_value', 3)
         ),
        ('vms[0].int_value', {'vms': [InnerViewModel(0, '')]},
         lambda gl: setattr(gl['vms'][0], 'int_value', 3)
         ),
        ('vms[ivm.int_value].int_value', {
            'vms': [InnerViewModel(0, ''), InnerViewModel(1, '')],
            'ivm': InnerViewModel(0, '')
        },
         lambda gl: setattr(gl['vms'][0], 'int_value', 3)
         ),
        ('vms[ivm.int_value].int_value', {
            'vms': [InnerViewModel(0, ''), InnerViewModel(1, '')],
            'ivm': InnerViewModel(0, '')
        },
         lambda gl: setattr(gl['ivm'], 'int_value', 1)
         )
    ]) # yapf: disable
    def test_expression_changed(self, source: str, global_dict: dict, change):
        """Target should be updated after expression result is changed"""
        expression = Expression(source)
        global_vars = NodeGlobals(global_dict)
        self._bind(expression, global_vars)

        change(global_vars)

        expected = execute(expression, global_vars)
        assert self.callback.call_args_list[1:] == [call(expected)]

    @mark.parametrize('source, global_dict, change', [
        ('vm.int_value', {'vm': InnerViewModel(0, '')},
         lambda gl: setattr(gl['vm'], 'int_value', 3)),
        ('vm.inner_vm.int_value', {'vm': ParentViewModel(0, InnerViewModel(0, ''))},
         lambda gl: setattr(gl['vm'], 'inner_vm', InnerViewModel(5, 'updated'))),
        ('vm.inner_vm.str_value', {'vm': ParentViewModel(0, InnerViewModel(0, ''))},
         lambda gl: setattr(gl['vm'].inner_vm, 'str_value', 'asdf')
         ),
        ('(vm.int_value, parent.inner_vm.int_value)',
         {'vm': InnerViewModel(0, ''),
          'parent': ParentViewModel(0, InnerViewModel(0, ''))},
         lambda gl: setattr(gl['parent'].inner_vm, 'int_value', 3)
         ),
        ('(vm.str_value, str(parent.inner_vm.int_value))',
         {'vm': InnerViewModel(0, ''),
          'parent': ParentViewModel(0, InnerViewModel(0, ''))},
         lambda gl: setattr(gl['parent'].inner_vm, 'int_value', 3)
         ),
        ('vms[0].int_value', {'vms': [InnerViewModel(0, '')]},
         lambda gl: setattr(gl['vms'][0], 'int_value', 3)
         ),
        ('vms[ivm.int_value].int_value', {
            'vms': [InnerViewModel(0, ''), InnerViewModel(1, '')],
            'ivm': InnerViewModel(0, '')
        },
         lambda gl: setattr(gl['vms'][0], 'int_value', 3)
         ),
        ('vms[ivm.int_value].int_value', {
            'vms': [InnerViewModel(0, ''), InnerViewModel(1, '')],
            'ivm': InnerViewModel(0, '')
        },
         lambda gl: setattr(gl['ivm'], 'int_value', 1)
         )
    ]) # yapf: disable
    def test_destroy(self, source: str, global_dict: dict, change):
        """Destroy should stop handling expression changes and update target"""
        expression = Expression(source)
        global_vars = NodeGlobals(global_dict)
        binding = self._bind(expression, global_vars)
        self.callback.reset_mock()

        binding.destroy()
        change(global_vars)

        assert not self.callback.called


@fixture
def binding_context_fixture(request):
    setter, xml_attr = Mock(), XmlAttr('name')
    context = BindingContext({
        'setter': setter,
        'xml_attr': xml_attr,
        'expression_body':
        '1+1',
        'node': Mock(node_globals = NodeGlobals())
    }) # yapf: disable

    request.cls.context = context


@mark.usefixtures('binding_context_fixture')
class BindSetterToExpressionTests:

    context: BindingContext

    def test_binds_setter_to_expression_changes(self):
        """should bind setter to expression changes"""
        self.context.node = Mock(node_globals = BindableDict({'value': 1}))
        self.context.expression_body = 'value'

        bind_setter_to_expression(self.context)
        self.context.setter.reset_mock()
        self.context.node.node_globals['value'] = 2

        assert self.context.setter.call_args == call(self.context.node, self.context.xml_attr.name, 2)

    def test_returns_binding(self):
        """should return expression binding"""
        actual = bind_setter_to_expression(self.context)

        assert isinstance(actual, ExpressionBinding)

@mark.parametrize('node_globals, expression, value, is_updated', [
    ({}, 'key', 2, lambda g: g['key'] == 2),
    ({'vm': ParentViewModel(1, None)}, 'vm.int_value', 2, lambda g: g['vm'].int_value == 2),
    ({
        'vm': ParentViewModel(1, InnerViewModel(2, 'init value'))},
        'vm.inner_vm.str_value', 'updated value',
        lambda g: g['vm'].inner_vm.str_value == 'updated value'
    ),
]) # yapf: disable
def test_get_expression_callback(node_globals, expression, value, is_updated):
    """get_expression_callback() tests"""
    node_globals = NodeGlobals(node_globals)
    parent_view_model = ParentViewModel(1, None)
    parent_view_model.int_value = 1
    callback = get_expression_callback(Expression(expression), node_globals)

    callback(value)

    assert is_updated(node_globals)
