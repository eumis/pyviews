from unittest import TestCase, main
from unittest.mock import patch, Mock
from tkinter import Entry
from pyviews.tk import parsing

class ParsingTests(TestCase):
    @patch('pyviews.tk.parsing.EntryWidget')
    def test_convert_to_entry_widget(self, entry_class):
        entry = Mock(spec=Entry)
        self._assert_created(entry, entry_class)

    @patch('pyviews.tk.parsing.WidgetNode')
    def test_convert_to_node(self, node_class):
        entry = Mock()
        self._assert_created(entry, node_class)

    def _assert_created(self, inst, node_class):
        args = {'xml_node': None, 'parent_context': None}

        parsing.convert_to_node(inst, args)

        self.assertTrue(node_class.called)

if __name__ == '__main__':
    main()
