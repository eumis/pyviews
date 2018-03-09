from unittest import TestCase, main
from unittest.mock import Mock, call
from pyviews.testing import case
from pyviews.core.observable import ObservableEntity, InheritedDict

class ObservableEnt(ObservableEntity):
    def __init__(self, private, name, value):
        super().__init__()
        self._private = private
        self.name = name
        self.value = value

    def get_private(self):
        return self._private

class ObservableEntityTests(TestCase):
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

class InheritedDictTests(TestCase):
    def setUp(self):
        parent = InheritedDict()
        parent['one'] = 1
        parent['two'] = 2
        self.parent = parent

        self.globs = InheritedDict(InheritedDict(parent))
        self.globs['two'] = 'two'
        self.globs['three'] = 'three'

    def test_globals_keys(self):
        self.assertEqual(self.globs['one'], 1, 'Globals should get values from parent')

        msg = 'Globals should get own value if key exists'
        self.assertEqual(self.globs['two'], 'two', msg)
        self.assertEqual(self.globs['three'], 'three', msg)

    def test_dictionary(self):
        msg = 'to_dictionary should return dictionary with all values'
        self.assertEqual(
            self.globs.to_dictionary(),
            {'one': 1, 'two': 'two', 'three': 'three'},
            msg)

    def test_remove_keys(self):
        self.globs.remove_key('two')
        self.globs.remove_key('three')

        msg = 'remove_key should remove own key'
        self.assertEqual(self.globs['two'], 2, msg)

        with self.assertRaises(KeyError, msg=msg):
            self.globs['three']

    @case('one', True)
    @case('two', True)
    @case('three', True)
    @case('key', False)
    def test_has_keys(self, key, expected):
        msg = 'has_key should return true for existant keys and false in other case'
        self.assertEqual(self.globs.has_key(key), expected, msg)

    @case('key')
    @case('hoho')
    @case('')
    @case(' ')
    def test_raises(self, key):
        with self.assertRaises(KeyError, msg='KeyError should be raised for unknown key'):
            self.globs[key]

    def test_notifying(self):
        callback = Mock()
        self.globs.observe('one', callback)
        self.parent['one'] = 2
        msg = 'change event should be raised if key changed in parent'
        self.assertTrue(callback.called, msg)

if __name__ == '__main__':
    main()
