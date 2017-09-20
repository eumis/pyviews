from unittest import TestCase, main
from pyviews.core.binding import PropertyGetRecorder
from pyviews.core.viewmodel import ViewModel

class InnerViewModel(ViewModel):
    def __init__(self, int_value, str_value):
        super().__init__()
        self.int_value = int_value
        self.str_value = str_value

class TestViewModel(ViewModel):
    def __init__(self, int_value, inner_vm):
        super().__init__()
        self.int_value = int_value
        self.inner_vm = inner_vm

class TestPropertyGetRecorder(TestCase):
    def setUp(self):
        self.inner_vm = InnerViewModel(1, 'str_value')
        self.vm = TestViewModel(1, self.inner_vm)
        self.recorder = PropertyGetRecorder(self.vm)

    def test_properties(self):        
        msg = 'recorder should return values from vm'
        self.assertEqual(self.recorder.int_value, self.vm.int_value, msg)
        self.assertEqual(self.recorder.inner_vm.int_value, self.vm.inner_vm.int_value, msg)
        self.assertEqual(self.recorder.inner_vm.str_value, self.vm.inner_vm.str_value, msg)

    def test_inner_vm(self):
        self.assertIsInstance(self.recorder.inner_vm, PropertyGetRecorder, 'recorder should replace inner ViewModel by recorder')

    def test_get_used_properties(self):
        self.recorder.int_value
        self.recorder.inner_vm.str_value

        used_properties = self.recorder.get_used_properties()

        msg = 'only view models with called properties should be returned'
        self.assertEqual(len(used_properties), 2, msg)
        self.assertTrue(self.vm in used_properties, msg)
        self.assertTrue(self.inner_vm in used_properties, msg)

        msg = 'only called properties should be returned'
        self.assertTrue('int_value' in used_properties[self.vm], msg)
        self.assertTrue('inner_vm' in used_properties[self.vm], msg)

        self.assertTrue('str_value' in used_properties[self.inner_vm], msg)

if __name__ == '__main__':
    main()
