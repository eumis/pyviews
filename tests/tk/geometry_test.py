from unittest import TestCase, main
from unittest.mock import Mock, call
from tests.utility import case
from pyviews.tk.geometry import GridGeometry, PackGeometry, PlaceGeometry
from pyviews.tk.geometry import Row, Column

class TestGridGeometry(TestCase):
    def setUp(self):
        self._widget = Mock()
        self._widget.grid = Mock()
        self._widget.grid_forget = Mock()

    def test_apply(self):
        geometry = GridGeometry()
        geometry.apply(self._widget)

        msg = 'apply method should call grid method of widget'
        self.assertTrue(self._widget.grid.called, msg)
        self.assertEqual(self._widget.grid.call_count, 1, msg)

    def test_forget(self):
        geometry = GridGeometry()
        geometry.forget(self._widget)

        msg = 'grid method should call grid_forget method of widget'
        self.assertTrue(self._widget.grid_forget.called, msg)
        self.assertEqual(self._widget.grid_forget.call_count, 1, msg)

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
        self._widget.pack_forget = Mock()

    def test_apply(self):
        geometry = PackGeometry()
        geometry.apply(self._widget)

        msg = 'apply method should call pack method of widget'
        self.assertTrue(self._widget.pack.called, msg)
        self.assertEqual(self._widget.pack.call_count, 1, msg)

    def test_forget(self):
        geometry = PackGeometry()
        geometry.forget(self._widget)

        msg = 'forget method should call pack_forget method of widget'
        self.assertTrue(self._widget.pack_forget.called, msg)

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

class TestPlaceGeometry(TestCase):
    def setUp(self):
        self._widget = Mock()
        self._widget.place = Mock()
        self._widget.place_forget = Mock()

    def test_apply(self):
        geometry = PlaceGeometry()
        geometry.apply(self._widget)

        msg = 'apply method should call pack method of widget'
        self.assertTrue(self._widget.place.called, msg)
        self.assertEqual(self._widget.place.call_count, 1, msg)

    def test_forget(self):
        geometry = PlaceGeometry()
        geometry.forget(self._widget)

        msg = 'forget method should call place_forget method of widget'
        self.assertTrue(self._widget.place_forget.called, msg)

    @case({})
    @case({'expand':True, 'fill':'x'})
    def test_init(self, args):
        geometry = PlaceGeometry(**args)
        geometry.apply(self._widget)

        msg = 'pack should be called with arguments passed to geometry'
        self.assertEqual(self._widget.place.call_args, call(**args), msg)

    @case({'expand':True})
    @case({'expand':True, 'fill':'x'})
    @case({'some_key':'value'})
    def test_set(self, args):
        geometry = PlaceGeometry()
        for key, value in args.items():
            geometry.set(key, value)
        geometry.apply(self._widget)

        msg = 'pack should be called with arguments passed to geometry'
        self.assertEqual(self._widget.place.call_args, call(**args), msg)

class TestRow(TestCase):
    def setUp(self):
        self._widget = Mock()
        self._widget.grid_rowconfigure = Mock()

    @case(0, {'minsize': 10})
    @case(2, {'weight': 5, 'minsize': 10})
    def test_apply(self, index, args):
        row = Row(self._widget, None)

        row.set_attr('index', index)
        for key, value in args.items():
            row.set_attr(key, value)
        row.apply()

        msg = 'Row.apply should be called with arguments set with set_attr'
        self.assertEqual(self._widget.grid_rowconfigure.call_args, call(index, **args), msg)

class TestColumn(TestCase):
    def setUp(self):
        self._widget = Mock()
        self._widget.grid_columnconfigure = Mock()

    @case(0, {'minsize': 10})
    @case(2, {'weight': 5, 'minsize': 10})
    def test_apply(self, index, args):
        column = Column(self._widget, None)

        column.set_attr('index', index)
        for key, value in args.items():
            column.set_attr(key, value)
        column.apply()

        msg = 'Column.apply should be called with arguments set with set_attr'
        self.assertEqual(self._widget.grid_columnconfigure.call_args, call(index, **args), msg)

if __name__ == '__main__':
    main()
