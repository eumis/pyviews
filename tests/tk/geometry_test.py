from unittest import TestCase, main
from unittest.mock import Mock, call
from tests.utility import case
from pyviews.tk.geometry import GridGeometry, PackGeometry

class TestGridGeometry(TestCase):
    def setUp(self):
        self._widget = Mock()
        self._widget.grid = Mock()

    def test_apply(self):
        geometry = GridGeometry()
        geometry.apply(self._widget)

        msg = 'apply method should call grid method of widget'
        self.assertTrue(self._widget.grid.called, msg)
        self.assertEqual(self._widget.grid.call_count, 1, msg)

    @case({})
    @case({'row':1, 'column':1})
    def test_init(self, args):
        geometry = GridGeometry(**args)
        geometry.apply(self._widget)

        msg = 'grid should be called with arguments passed to geometry'
        self.assertEqual(self._widget.grid.call_args, call(**args), msg)

    @case({'row':1})
    @case({'row':1, 'column':2})
    @case({'some_key':'value'})
    def test_set(self, args):
        geometry = GridGeometry()
        for key, value in args.items():
            geometry.set(key, value)
        geometry.apply(self._widget)

        msg = 'grid should be called with arguments passed to geometry'
        self.assertEqual(self._widget.grid.call_args, call(**args), msg)

class TestPackGeometry(TestCase):
    def setUp(self):
        self._widget = Mock()
        self._widget.pack = Mock()

    def test_apply(self):
        geometry = PackGeometry()
        geometry.apply(self._widget)

        msg = 'apply method should call pack method of widget'
        self.assertTrue(self._widget.pack.called, msg)
        self.assertEqual(self._widget.pack.call_count, 1, msg)

    @case({})
    @case({'expand':True, 'fill':'x'})
    def test_init(self, args):
        geometry = PackGeometry(**args)
        geometry.apply(self._widget)

        msg = 'pack should be called with arguments passed to geometry'
        self.assertEqual(self._widget.pack.call_args, call(**args), msg)

    @case({'expand':True})
    @case({'expand':True, 'fill':'x'})
    @case({'some_key':'value'})
    def test_set(self, args):
        geometry = PackGeometry()
        for key, value in args.items():
            geometry.set(key, value)
        geometry.apply(self._widget)

        msg = 'pack should be called with arguments passed to geometry'
        self.assertEqual(self._widget.pack.call_args, call(**args), msg)

if __name__ == '__main__':
    main()
