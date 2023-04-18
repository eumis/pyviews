from unittest.mock import Mock, call

from pytest import fixture, mark, raises

from pyviews.core.bindable import BindableDict, BindableEntity, BindableRecord, recording


class TestBindable(BindableEntity):

    def __init__(self, private, name, value):
        super().__init__()
        self._private = private
        self.name = name
        self.value = value

    def get_private(self):
        return self._private


@fixture
def observable_fixture(request):
    request.cls.observable = TestBindable('private', 'some name', 'some value')
    request.cls.callback = Mock()
    request.cls.add_callback = Mock()


@mark.usefixtures('observable_fixture')
class BindableEntityTests:
    """BindableEntity class tests"""

    observable: TestBindable
    callback: Mock
    add_callback: Mock

    def test_observe(self):
        """observe() should subscribe passed callback to property changes"""
        self.observable.observe('name', self.callback)

        self.observable.name = 'new name'
        self.observable.value = 'new value'

        assert self.callback.call_count == 1
        assert self.callback.call_args == call('new name', 'some name')

    def test_observe_raises(self):
        """observe() should raise if entity doesn't have passed property"""
        with raises(KeyError):
            self.observable.observe('attr', self.callback)

    def test_release_callback(self):
        """release() should unsubscribe callback from property changes"""
        new_name = "new name"
        old_value, new_value = self.observable.value, "new value"
        self.observable.observe('name', self.callback)
        self.observable.observe('value', self.callback)

        self.observable.release('name', self.callback)
        self.observable.name = new_name
        self.observable.value = new_value

        assert self.callback.call_count == 1
        assert self.callback.call_args == call(new_value, old_value)

    def test_release_callback_releases_same_callbacks(self):
        """release() should unsubscribe same callbacks from property changes"""
        new_name = "new name"
        self.observable.observe('name', self.callback)
        self.observable.observe('name', self.callback)

        self.observable.release('name', self.callback)
        self.observable.name = new_name

        assert not self.callback.called

    def test_observe_in_callback(self):
        """observe() inside callback should add new callback"""
        self.observable.observe('name', lambda *_: self.observable.observe('name', self.callback))

        self.observable.name = 'new name'
        assert self.callback.call_count == 0

        self.observable.name = 'another name'
        assert self.callback.call_count == 1

    def test_recording(self):
        one = TestBindable('one', 'one', 'one')
        one.value = 'value'
        with recording() as records:
            self.observable.name = 'new name'

            two = TestBindable('two', 'two', 2)
            two.value = 5
        one.name = 'updated name'

        print('----------records-------------')
        for rec in records:
            print(f'hash {hash(rec)} id {id(rec.bindable)} key {rec.key}')
        print('----------items-------------')
        for rec in [BindableRecord(self.observable, 'name'), BindableRecord(two, 'value')]:
            print(f'hash {hash(rec)} id {id(rec.bindable)} key {rec.key}')
        assert records == {BindableRecord(self.observable, 'name'), BindableRecord(two, 'value')}


class BindableDictTests:

    @staticmethod
    def _create_inh_dict(own, parent):
        inh_dict = BindableDict(own)
        if parent:
            inh_dict.inherit(parent)
        return inh_dict

    @staticmethod
    @mark.parametrize('source', [{}, {'key': 'value'}, {'key': 'value', 'two': 1}, ])
    def test_dict_source(source):
        """__init__() should copy values from source dict"""
        inh_dict = BindableDict(source)

        assert inh_dict == source

    @staticmethod
    def test_notifying_on_change():
        """__setitem__() should notify subscribers"""
        inh_dict = BindableDict()
        key, callback = 'key', Mock()
        inh_dict.observe(key, callback)

        inh_dict[key] = 2

        assert callback.call_args == call(2, None)

    @staticmethod
    def test_notifying_on_delete():
        """__delitem__() should notify subscribers"""
        key, value = 'key', 2
        callback, all_callback = Mock(), Mock()
        inh_dict = BindableDict({key: value})
        inh_dict.observe(key, callback)
        inh_dict.observe_all(all_callback)

        del inh_dict[key]

        assert key not in inh_dict
        assert callback.call_args == call(None, value)
        assert all_callback.call_args == call(key, None, value)

    @staticmethod
    def test_notifying_on_pop():
        """pop() should notify subscribers"""
        key, value = 'key', 2
        callback, all_callback = Mock(), Mock()
        inh_dict = BindableDict({key: value})
        inh_dict.observe(key, callback)
        inh_dict.observe_all(all_callback)

        pop_value = inh_dict.pop(key)
        default_pop_value = inh_dict.pop(key, 'default')

        assert key not in inh_dict
        assert pop_value == value
        assert default_pop_value == 'default'
        assert callback.call_args == call(None, value)
        assert all_callback.call_args == call(key, None, value)

    @staticmethod
    def test_observe_all():
        """observe_all() should subscribe callback to all existing values changes and new values adding"""
        inherited_dict = BindableDict()
        callback = Mock()

        inherited_dict.observe_all(callback)

        inherited_dict['name'] = 'new name'
        inherited_dict['value'] = 'new value'

        assert callback.call_args_list == [call('name', 'new name', None), call('value', 'new value', None)]

    @staticmethod
    def test_release_all():
        """release_all() should remove callback subscription to all changes"""
        inherited_dict = BindableDict()
        callback = Mock()
        active_callback = Mock()
        inherited_dict.observe_all(callback)
        inherited_dict.observe_all(active_callback)

        inherited_dict.release_all(callback)
        inherited_dict['name'] = 'new name'
        inherited_dict['value'] = 'new value'

        assert active_callback.called
        assert not callback.called

    @staticmethod
    def test_release_all_same_callback():
        """release_all() should remove callback subscription to all changes"""
        inherited_dict = BindableDict()
        callback = Mock()
        inherited_dict.observe_all(callback)
        inherited_dict.observe_all(callback)

        inherited_dict.release_all(callback)
        inherited_dict['name'] = 'new name'
        inherited_dict['value'] = 'new value'

        assert not callback.called

    @staticmethod
    def test_recording():
        source = {'name': 'some name', 'value': 5}
        one = BindableDict(source)
        _ = one['value']
        with recording() as records:
            two, three = BindableDict(source), BindableDict(source)

            _ = two['name']
            _ = three.get('value')
            _ = three.get('other', None)

        _ = one['name']

        assert records == {BindableRecord(two, 'name'), BindableRecord(three, 'value'), BindableRecord(three, 'other')}
