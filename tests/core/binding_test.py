from unittest import TestCase, main
from tests.utility import case
from pyviews.core.binding import *
from pyviews.core.compilation import Expression, IhertiedDict
from pyviews.core.observable import ObservableEntity

class InnerViewModel(ObservableEntity):
    def __init__(self, int_value, str_value):
        super().__init__()
        self.int_value = int_value
        self.str_value = str_value

    def to_string(self):
        return str(self.int_value) + self.str_value

class ParentViewModel(ObservableEntity):
    def __init__(self, int_value, inner_vm):
        super().__init__()
        self.int_value = int_value
        self.inner_vm = inner_vm
        self.another_vm = inner_vm

    def to_string(self):
        return str(self.int_value)

class SomeEntity:
    def __init__(self):
        self.int_value = 1
        self.str_value = 'str'

class TestInstanceTarget(TestCase):
    def test_set_value(self):
        inst = SomeEntity()
        target = InstanceTarget(inst, 'int_value', setattr)
        new_val = 25

        target.set_value(new_val)

        msg = 'set_value should return expression result value'
        self.assertEqual(inst.int_value, new_val, msg)

class TestBindingWithSimpleExpression(TestCase):
    def setUp(self):
        
        self.view_model = InnerViewModel(2, 'inner str')
        self.expression = Expression('str(vm.int_value) + vm.str_value')
        self.inst = SomeEntity()
        self.target = InstanceTarget(self.inst, 'str_value', setattr)
        self.binding = ExpressionBinding(self.target, self.expression)
        self.vars = IhertiedDict()
        self.vars['vm'] = self.view_model

    def test_binding_creation(self):
        self.binding.bind(self.vars)

        msg = 'property should be updated on binding creation'
        actual = str(self.view_model.int_value) + self.view_model.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

    def test_binding(self):
        self.binding.bind(self.vars)

        msg = 'property should be updated on vm change'

        self.view_model.int_value = 3
        actual = str(self.view_model.int_value) + self.view_model.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

        self.view_model.str_value = 'new str value'
        actual = str(self.view_model.int_value) + self.view_model.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

    def test_destroy(self):
        self.binding.bind(self.vars)

        expected = self.inst.str_value
        self.binding.destroy()

        msg = 'destroy should remove property change on expression change'

        self.view_model.int_value = 3
        self.assertEqual(self.inst.str_value, expected, msg)

        self.view_model.str_value = 'new str value'
        self.assertEqual(self.inst.str_value, expected, msg)

class TestBindingWithInnerViewModel(TestCase):
    def setUp(self):
        inner_vm = InnerViewModel(2, 'inner str')
        self.view_model = ParentViewModel(3, inner_vm)
        self.expression = Expression('str(vm.int_value) + vm.inner_vm.str_value')
        self.inst = SomeEntity()
        self.target = InstanceTarget(self.inst, 'str_value', setattr)
        self.binding = ExpressionBinding(self.target, self.expression)
        self.vars = IhertiedDict()
        self.vars['vm'] = self.view_model

    def test_binding(self):
        self.binding.bind(self.vars)

        msg = 'property should be updated on vm change'
        self.view_model.int_value = 3
        actual = str(self.view_model.int_value) + self.view_model.inner_vm.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

        msg = 'property should be updated on inner vm change'
        self.view_model.inner_vm.str_value = 'new str value'
        actual = str(self.view_model.int_value) + self.view_model.inner_vm.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

        msg = 'property should be updated on inner vm change'
        self.view_model.inner_vm = InnerViewModel(50, 'new inner value')
        actual = str(self.view_model.int_value) + self.view_model.inner_vm.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

        msg = 'property should be updated on inner vm property change'
        self.view_model.inner_vm.str_value = 'new str value'
        actual = str(self.view_model.int_value) + self.view_model.inner_vm.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

class TestExpressionTarget(TestCase):
    def setUp(self):
        self.inner = InnerViewModel(1, '1')
        self.parent = ParentViewModel(1, self.inner)
        self.expr_vars = IhertiedDict()
        self.expr_vars['vm'] = self.parent

    @case('vm')
    @case('vm.int_value + val')
    def test_raises(self, expression):
        with self.assertRaises(ValueError):
            ExpressionTarget(Expression(expression))

    def test_set_value(self):
        target = ExpressionTarget(Expression("vm.int_value"))
        new_val = 25

        target.set_value(self.expr_vars, new_val)

        msg = 'set_value should return expression result value'
        self.assertEqual(self.parent.int_value, new_val, msg)

    def test_set_inner_value(self):
        target = ExpressionTarget(Expression('vm.inner_vm.int_value'))
        new_val = 26
        target.set_value(self.expr_vars, new_val)

        msg = 'set_value should return expression result value'
        self.assertEqual(self.parent.inner_vm.int_value, new_val, msg)

class TestObservableBinding(TestCase):
    def setUp(self):
        self.expression = Expression('vm.int_value')
        self.expr_inst = InnerViewModel(1, '1')
        self.inst = InnerViewModel(1, '1')
        self.converter = lambda value: str(value)
        target = ExpressionTarget(self.expression)
        self.binding = ObservableBinding(target, self.inst, 'int_value', self.converter)
        self.expr_vars = IhertiedDict()
        self.expr_vars['vm'] = self.expr_inst

    def test_binding(self):
        self.binding.bind(self.expr_vars)

        new_val = 2
        self.inst.int_value = new_val

        msg = 'property from expression should be updated on instance updating'
        self.assertEqual(self.expr_inst.int_value, str(new_val), msg)

    def test_destroy(self):
        self.binding.bind(self.expr_vars)

        self.binding.destroy()
        self.inst.int_value = self.inst.int_value + 2

        msg = 'property from expression shouldn''t be updated after binding destroying'
        self.assertNotEqual(self.expr_inst, self.inst.int_value, msg)

class TestTwoWaysBinding(TestCase):
    def setUp(self):
        self.expression = Expression('vm.int_value')
        self.expr_inst = InnerViewModel(1, '1')
        self.inst = InnerViewModel(1, '1')
        self.binding = TwoWaysBinding(self.inst, 'int_value', setattr, None, self.expression)
        self.expr_vars = IhertiedDict()
        self.expr_vars['vm'] = self.expr_inst

    def test_property_binding(self):
        self.binding.bind(self.expr_vars)

        new_val = 2
        self.inst.int_value = new_val

        msg = 'property from expression should be updated on instance updating'
        self.assertEqual(self.expr_inst.int_value, new_val, msg)

    def test_property_binding_destroy(self):
        self.binding.bind(self.expr_vars)

        self.binding.destroy()
        self.inst.int_value = self.inst.int_value + 2

        msg = 'property from expression shouldn''t be updated after binding destroying'
        self.assertNotEqual(self.expr_inst, self.inst.int_value, msg)

    def test_expression_binding(self):
        self.binding.bind(self.expr_vars)

        new_val = 2
        self.expr_inst.int_value = new_val

        msg = 'property should be updated on vm change'
        self.assertEqual(self.inst.int_value, new_val, msg)

    def test_expression_binding_destroy(self):
        self.binding.bind(self.expr_vars)

        self.binding.destroy()
        self.expr_inst.int_value = self.expr_inst.int_value + 2

        msg = 'destroy should remove property change on expression change'
        self.assertNotEqual(self.inst, self.expr_inst.int_value, msg)

if __name__ == '__main__':
    main()
