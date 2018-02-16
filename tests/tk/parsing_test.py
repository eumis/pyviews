from unittest import TestCase, main
from unittest.mock import patch, Mock
from tkinter import Entry
from tests.utility import case
from pyviews.tk import rendering as parsing

class ParsingTests(TestCase):
    @patch('pyviews.tk.rendering.parse_attr')
    @case(None)
    @case('')
    def test_apply_text_none(self, parse_attr, text):
        node = Mock()
        node.xml_node = Mock()
        node.xml_node.text = text

        parsing.apply_text(node)

        msg = "parse_attr shouldn't be called if text is None"
        self.assertFalse(parse_attr.called, msg)

    @patch('pyviews.tk.rendering.parse_attr')
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
