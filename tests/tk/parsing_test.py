from unittest import TestCase, main
from unittest.mock import patch, Mock
from tkinter import Entry
from tests.utility import case
from pyviews.tk import parsing

class ParsingTests(TestCase):
    @patch('pyviews.tk.parsing.EntryWidget')
    def test_convert_to_entry_widget(self, entry_class):
        entry = Mock(spec=Entry)

        msg = "tkinter.Entry should be converted to EntryWidget"
        self._assert_created(entry, entry_class, msg)

    @patch('pyviews.tk.parsing.WidgetNode')
    def test_convert_to_node(self, node_class):
        entry = Mock()

        msg = "instance should be converted to WidgetNode by default"
        self._assert_created(entry, node_class, msg)

    def _assert_created(self, inst, node_class, msg):
        args = {'xml_node': None, 'parent_context': None}

        parsing.convert_to_node(inst, args)

        self.assertTrue(node_class.called, msg)

    @patch('pyviews.tk.parsing.parse_attr')
    @case(None)
    @case('')
    def test_apply_text_none(self, parse_attr, text):
        node = Mock()
        node.xml_node = Mock()
        node.xml_node.text = text

        parsing.apply_text(node)

        msg = "parse_attr shouldn't be called if text is None"
        self.assertFalse(parse_attr.called, msg)

    @patch('pyviews.tk.parsing.parse_attr')
    @case('  ')
    @case('asdfasdf')
    def test_apply_text(self, parse_attr, text):
        node = Mock()
        node.xml_node = Mock()
        node.xml_node.text = text

        parsing.apply_text(node)

        msg = 'parse_attr should be called with XmlAttr "text"'
        self.assertEqual(parse_attr.call_args[0][0], node, msg)

        msg = 'parse_attr should be called with XmlAttr "text"'
        attr = parse_attr.call_args[0][1]
        self.assertEqual(attr.name, 'text', msg)
        self.assertEqual(attr.value, text, msg)

if __name__ == '__main__':
    main()
