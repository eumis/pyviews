# pylint: disable=missing-docstring

from unittest import TestCase
from pyviews.testing import case
from pyviews.core import ObservableEntity, InheritedDict, BindingError
from pyviews.compilation import CompiledExpression
from .implementations import PropertyTarget, FunctionTarget
from .implementations import PropertyExpressionTarget, GlobalValueExpressionTarget
from .implementations import ExpressionBinding, ObservableBinding, TwoWaysBinding

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

class InstanceTargetTests(TestCase):
    def test_on_change(self):
        inst = SomeEntity()
        target = PropertyTarget(inst, 'int_value', setattr)
        new_val = 25

        target.on_change(new_val)

        msg = 'change should return expression result value'
        self.assertEqual(inst.int_value, new_val, msg)

class FunctionTargetTests(TestCase):
    def test_on_change(self):
        inst = SomeEntity()
        target = FunctionTarget(lambda value: setattr(inst, 'int_value', value))
        new_val = 25

        target.on_change(new_val)

        msg = 'change should return expression result value'
        self.assertEqual(inst.int_value, new_val, msg)

class BindingWithSimpleExpressionTests(TestCase):
    def setUp(self):
        self.view_model = InnerViewModel(2, 'inner str')
        self.expression = CompiledExpression('str(vm.int_value) + vm.str_value')
        self.inst = SomeEntity()
        self.vars = InheritedDict()
        self.vars['vm'] = self.view_model
        self.target = PropertyTarget(self.inst, 'str_value', setattr)
        self.binding = ExpressionBinding(self.target, self.expression, self.vars)

    def test_binding_creation(self):
        self.binding.bind()

        msg = 'property should be updated on binding creation'
        actual = str(self.view_model.int_value) + self.view_model.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

    def test_binding(self):
        self.binding.bind()

        msg = 'property should be updated on vm change'

        self.view_model.int_value = 3
        actual = str(self.view_model.int_value) + self.view_model.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

        self.view_model.str_value = 'new str value'
        actual = str(self.view_model.int_value) + self.view_model.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

    def test_destroy(self):
        self.binding.bind()

        expected = self.inst.str_value
        self.binding.destroy()

        msg = 'destroy should remove property change on expression change'

        self.view_model.int_value = 3
        self.assertEqual(self.inst.str_value, expected, msg)

        self.view_model.str_value = 'new str value'
        self.assertEqual(self.inst.str_value, expected, msg)

class ExpressionBindingTests(TestCase):
    def setUp(self):
        inner_vm = InnerViewModel(2, 'inner str')
        self.view_model = ParentViewModel(3, inner_vm)
        self.expression = CompiledExpression('str(vm.int_value) + vm.inner_vm.str_value + vm.get_val() + vm.inner_vm.get_val()')
        self.inst = SomeEntity()
        self.vars = InheritedDict()
        self.vars['vm'] = self.view_model
        self.target = PropertyTarget(self.inst, 'str_value', setattr)
        self.binding = ExpressionBinding(self.target, self.expression, self.vars)

    @case(lambda vm: setattr(vm, 'int_value', 3))
    @case(lambda vm: setattr(vm.inner_vm, 'str_value', 'new str value'))
    @case(lambda vm: setattr(vm, 'inner_vm', InnerViewModel(50, 'new inner value')))
    @case(lambda vm: setattr(vm.inner_vm, 'str_value', 'new str value'))
    @case(lambda vm: vm.set_val('asdf'))
    @case(lambda vm: vm.inner_vm.set_val('asdf'))
    def test_binding(self, change):
        self.binding.bind()

        msg = 'property should be updated on expression change'
        change(self.view_model)
        actual = str(self.view_model.int_value) + self.view_model.inner_vm.str_value \
                 + self.view_model.get_val() + self.view_model.inner_vm.get_val()
        self.assertEqual(self.inst.str_value, actual, msg)

class PropertyExpressionTargetTests(TestCase):
    def setUp(self):
        self.inner = InnerViewModel(1, '1')
        self.parent = ParentViewModel(1, self.inner)
        self.expr_vars = InheritedDict()
        self.expr_vars['vm'] = self.parent

    @case('vm')
    @case('vm.int_value + val')
    def test_raises(self, expression):
        with self.assertRaises(BindingError):
            PropertyExpressionTarget(CompiledExpression(expression), self.expr_vars)

    def test_change(self):
        target = PropertyExpressionTarget(CompiledExpression("vm.int_value"), self.expr_vars)
        new_val = 25

        target.on_change(new_val)

        msg = 'change should return expression result value'
        self.assertEqual(self.parent.int_value, new_val, msg)

    def test_set_inner_value(self):
        target = PropertyExpressionTarget(CompiledExpression('vm.inner_vm.int_value'), self.expr_vars)
        new_val = 26
        target.on_change(new_val)

        msg = 'change should return expression result value'
        self.assertEqual(self.parent.inner_vm.int_value, new_val, msg)

class GlobalValueExpressionTargetTests(TestCase):
    def setUp(self):
        self.expr_vars = InheritedDict()
        self.expr_vars['vm'] = 1

    @case('vm.int_value')
    @case('vm + val')
    def test_raises(self, expression):
        with self.assertRaises(BindingError):
            GlobalValueExpressionTarget(CompiledExpression(expression), self.expr_vars)

    def test_change(self):
        target = GlobalValueExpressionTarget(CompiledExpression("vm"), self.expr_vars)
        new_val = 25

        target.on_change(25)

        msg = 'change should return expression result value'
        self.assertEqual(self.expr_vars['vm'], new_val, msg)

class ObservableBindingTests(TestCase):
    def setUp(self):
        self.expression = CompiledExpression('vm.int_value')
        self.expr_inst = InnerViewModel(1, '1')
        self.inst = InnerViewModel(1, '1')
        self.expr_vars = InheritedDict()
        self.expr_vars['vm'] = self.expr_inst
        target = PropertyExpressionTarget(self.expression, self.expr_vars)
        self.binding = ObservableBinding(target, self.inst, 'int_value')

    def test_binding(self):
        self.binding.bind()

        new_val = 2
        self.inst.int_value = new_val

        msg = 'property from expression should be updated on instance updating'
        self.assertEqual(self.expr_inst.int_value, new_val, msg)

    def test_destroy(self):
        self.binding.bind()

        self.binding.destroy()
        self.inst.int_value = self.inst.int_value + 2

        msg = 'property from expression shouldn''t be updated after binding destroying'
        self.assertNotEqual(self.expr_inst, self.inst.int_value, msg)

class TwoWaysBindingTests(TestCase):
    def setUp(self):
        self.expression = CompiledExpression('vm.int_value')
        self.expr_inst = InnerViewModel(1, '1')
        self.inst = InnerViewModel(1, '1')
        self.expr_vars = InheritedDict()
        self.expr_vars['vm'] = self.expr_inst

        target = PropertyTarget(self.inst, 'int_value', setattr)
        one_binding = ExpressionBinding(target, self.expression, self.expr_vars)

        target = PropertyExpressionTarget(self.expression, self.expr_vars)
        two_binding = ObservableBinding(target, self.inst, 'int_value')

        self.binding = TwoWaysBinding(one_binding, two_binding)

    def test_property_binding(self):
        self.binding.bind()

        new_val = 2
        self.inst.int_value = new_val

        msg = 'property from expression should be updated on instance updating'
        self.assertEqual(self.expr_inst.int_value, new_val, msg)

    def test_property_binding_destroy(self):
        self.binding.bind()

        self.binding.destroy()
        self.inst.int_value = self.inst.int_value + 2

        msg = 'property from expression shouldn''t be updated after binding destroying'
        self.assertNotEqual(self.expr_inst, self.inst.int_value, msg)

    def test_expression_binding(self):
        self.binding.bind()

        new_val = 2
        self.expr_inst.int_value = new_val

        msg = 'property should be updated on vm change'
        self.assertEqual(self.inst.int_value, new_val, msg)

    def test_expression_binding_destroy(self):
        self.binding.bind()

        self.binding.destroy()
        self.expr_inst.int_value = self.expr_inst.int_value + 2

        msg = 'destroy should remove property change on expression change'
        self.assertNotEqual(self.inst, self.expr_inst.int_value, msg)
