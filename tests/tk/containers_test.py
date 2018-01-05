from unittest import TestCase, main
from unittest.mock import Mock, call
from tests.utility import case
from pyviews.tk.containers import Container, View, For

class ContainerTest(TestCase):
    def setUp(self):
        self.container = Container(None, None)
        self.container.property = None

    def test_set_attr(self):
        value = 'value'
        self.container.set_attr('property', value)

        msg = 'set_attr should set container property'
        self.assertEqual(self.container.property, value, msg)

    def test_view_model_stored_in_globals(self):
        view_model = 'view model'
        self.container.view_model = view_model

        msg = 'view_model property should be stored in globals'
        self.assertEqual(self.container.globals['vm'], view_model, msg)

class ViewTest(TestCase):
    def setUp(self):
        self.view = View(None, None)
        self.view.parse_children = Mock()

    def test_name_change(self):
        self.view.name = 'view'

        msg = 'parse_children should be called on name change'
        self.assertTrue(self.view.parse_children.called, msg)

    def test_same_name_passed(self):
        view_name = 'view'
        self.view.name = view_name
        self.view.name = view_name

        msg = 'parse_children should be called if passed name is not the same as curren'
        self.assertEqual(self.view.parse_children.call_count, 1, msg)

if __name__ == '__main__':
    main()
