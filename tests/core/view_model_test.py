from unittest import TestCase, main
from unittest.mock import Mock, call
from tests.mock import TestViewModel as ViewModel

class TestViewModel(TestCase):
    def test_get_observable_keys(self):
        view_model = ViewModel('priv', 'some name', 'some value')
        keys = view_model.get_observable_keys()

        msg = 'ViewModel should use public properties as observable'
        expected_keys = [
            'name', 'value', 'observe',
            'release_callback', 'get_observable_keys', 'get_private']
        self.assertListEqual(sorted(keys), sorted(expected_keys), msg)

    def test_observe(self):
        view_model = ViewModel('priv', 'some name', 'some value')
        callback = Mock()
        callback.call_args_list
        view_model.observe('name', callback)

        view_model.name = 'new name'
        view_model.value = 'new value'

        msg = 'callback should be called on observed property change'
        self.assertTrue(callback.called, msg)
        self.assertEqual(callback.call_count, 1, msg)

        msg = '(new value, old value) args should be passed to callback'
        self.assertEqual(callback.call_args, call('new name', 'some name'), msg)

    def test_release_callback(self):
        view_model = ViewModel('priv', 'some name', 'some value')
        callback = Mock()
        callback.call_args_list
        view_model.observe('name', callback)
        view_model.observe('value', callback)

        view_model.release_callback('name', callback)
        view_model.name = 'new name'
        view_model.value = 'new value'

        msg = 'callback should be called on observed property change'
        self.assertTrue(callback.called, msg)

        msg = 'callback shouldn''t be called after realeasing'
        self.assertEqual(callback.call_count, 1, msg)

        msg = 'callback should be called only for observed properties'
        self.assertEqual(callback.call_args, call('new value', 'some value'), msg)

if __name__ == '__main__':
    main()
