from unittest import TestCase, main
from unittest.mock import Mock, call
from pyviews.core.observable import ObservableEntity

class ObservableEnt(ObservableEntity):
    def __init__(self, private, name, value):
        super().__init__()
        self._private = private
        self.name = name
        self.value = value

    def get_private(self):
        return self._private

class TestObservableEntity(TestCase):
    def setUp(self):
        self.observable = ObservableEnt('priv', 'some name', 'some value')
        self.callback = Mock()
        self.add_callback = Mock()
        self.add_callback.side_effect = self._add_name_callback

    def _add_name_callback(self, *args):
        self.observable.observe('name', self.callback)

    def test_observe(self):
        self.observable.observe('name', self.callback)

        self.observable.name = 'new name'
        self.observable.value = 'new value'

        msg = 'self.callback should be called on observed property change'
        self.assertTrue(self.callback.called, msg)
        self.assertEqual(self.callback.call_count, 1, msg)

        msg = '(new value, old value) args should be passed to self.callback'
        self.assertEqual(self.callback.call_args, call('new name', 'some name'), msg)

    def test_observe_all(self):
        self.observable.observe_all(self.callback)

        self.observable.name = 'new name'
        self.observable.value = 'new value'

        msg = 'self.callback should be called on observed property change'
        self.assertTrue(self.callback.called, msg)
        self.assertEqual(self.callback.call_count, 2, msg)

        msg = '(new value, old value) args should be passed to self.callback'

    def test_observe_raises(self):
        with self.assertRaises(KeyError, msg='ObservableEntity should raise for unknown attribute'):
            self.observable.observe('attr', lambda: self.callback)

    def test_release_callback(self):
        self.observable.observe('name', self.callback)
        self.observable.observe('value', self.callback)

        self.observable.release('name', self.callback)
        self.observable.name = 'new name'
        self.observable.value = 'new value'

        msg = 'self.callback should be called on observed property change'
        self.assertTrue(self.callback.called, msg)

        msg = 'self.callback shouldn''t be called after realeasing'
        self.assertEqual(self.callback.call_count, 1, msg)

        msg = 'self.callback should be called only for observed properties'
        self.assertEqual(self.callback.call_args, call('new value', 'some value'), msg)

    def test_release_all_callback(self):
        active_callback = Mock()
        self.observable.observe_all(self.callback)
        self.observable.observe_all(active_callback)

        self.observable.release_all(self.callback)
        self.observable.name = 'new name'
        self.observable.value = 'new value'

        msg = 'released callbacks shouldn''t be called'
        self.assertTrue(active_callback.called, msg)
        self.assertFalse(self.callback.called, msg)

    def test_observe_in_callback(self):
        self.observable.observe('name', self.add_callback)
        self.observable.name = 'new name'

        msg = 'only callbacks registered before assignment should be called'
        self.assertEqual(self.add_callback.call_count, 1, msg=msg)
        msg = 'callbacks registered in another callback shouldn''t be called'
        self.assertEqual(self.callback.call_count, 0, msg=msg)

        self.observable.name = 'another name'
        msg = 'only callbacks registered before assignment should be called'
        self.assertEqual(self.add_callback.call_count, 2, msg=msg)
        msg = 'callbacks registered in another callback should be called'
        self.assertEqual(self.callback.call_count, 1, msg=msg)

    def test_observe_all_in_callback(self):
        self.observable.observe_all(self.add_callback)
        self.observable.name = 'new name'

        msg = 'only callbacks registered before assignment should be called'
        self.assertEqual(self.add_callback.call_count, 1, msg=msg)
        msg = 'callbacks registered in another callback shouldn''t be called'
        self.assertEqual(self.callback.call_count, 0, msg=msg)

        self.observable.name = 'another name'
        msg = 'only callbacks registered before assignment should be called'
        self.assertEqual(self.add_callback.call_count, 2, msg=msg)
        msg = 'callbacks registered in another callback should be called'
        self.assertEqual(self.callback.call_count, 1, msg=msg)

if __name__ == '__main__':
    main()
