from unittest import TestCase, main
from unittest.mock import call, Mock
from tests.utility import case
from tests.mock import some_modifier
from pyviews.core.ioc import CONTAINER
from pyviews.core.xml import XmlAttr
from pyviews.core.compilation import InheritedDict
from pyviews.tk.styles import StyleItem, Style, parse_attrs, apply_styles

class StyleItemTest(TestCase):
    @case('key', 1)
    @case('asdf', None)
    @case('', None)
    @case('', 1)
    def test_apply_should_call_modifier(self, name, value):
        modifier = Mock()
        item = StyleItem(modifier, name, value)
        node = Mock()

        item.apply(node)

        msg = 'apply should call passed modifier with parameters'
        self.assertEqual(modifier.call_args, call(node, name, value), msg)

class StyleTest(TestCase):
    def setUp(self):
        self.context = {'styles': InheritedDict()}
        self.style = Style(None, self.context)

    @case('name', [])
    @case('other_name', [StyleItem(None, None, None)])
    def test_set_items_should_set_to_passed_context(self, name, items):
        self.style.name = name
        self.style.set_items(items)

        msg = 'set_items should add passed items to context'
        self.assertEqual(items, self.context['styles'][name], msg)

    @case('')
    @case(None)
    def test_set_items_should_raise_if_name_is_not_set(self, name):
        self.style.name = name

        msg = 'set_items should raise error if name is not set'
        with self.assertRaises(Exception, msg=msg):
            self.style.set_items([])

    def test_destroy_should_remove_styles_from_context(self):
        self.style.name = 'name'
        self.style.set_items([])

        self.style.destroy()

        msg = 'destroy should remove items from context'
        self.assertFalse(self.context['styles'].has_key(self.style.name), msg)

DEFAULT_MODIFIER = CONTAINER.get('set_attr')

class ParsingTest(TestCase):
    def setUp(self):
        pass

    @case([('name', 'some_style'),
           ('key', 'value'),
           ('{tests.core.parsing_test.some_modifier}key', 'other_value'),
           ('num', '{1}'),
           ('num', '{count}'),
           ('bg', '#000')],
          [StyleItem(DEFAULT_MODIFIER, 'key', 'value'),
           StyleItem(some_modifier, 'key', 'other_value'),
           StyleItem(DEFAULT_MODIFIER, 'num', 1),
           StyleItem(DEFAULT_MODIFIER, 'num', 2),
           StyleItem(DEFAULT_MODIFIER, 'bg', '#000')],
          {'count': 2})
    def test_parse_attrs_creates_style_items(self, attrs, style_items, global_values):
        xml_node = Mock()
        xml_node.get_attrs = Mock(return_value=[XmlAttr(attr) for attr in attrs])
        parent_globals = InheritedDict()
        for key, value in global_values.items():
            parent_globals[key] = value
        context = {'styles': InheritedDict(), 'globals': parent_globals}
        style = Style(xml_node, context)

        parse_attrs(style)

        msg = 'actual style_items are not equal to expected'
        self.assertTrue(self._style_items_equal(style_items, context['styles'][style.name]), msg)

    def _style_items_equal(self, expected, actual):
        if len(expected) != len(actual):
            return False

        for i, item in enumerate(expected):
            result_item = actual[i]
            if item._modifier != result_item._modifier \
               or item._name != result_item._name \
               or item._value != result_item._value:
                return False

        return True

    @case('name')
    @case('some name')
    def test_parse_attrs_sets_style_name(self, name):
        xml_node = Mock()
        xml_node.get_attrs = Mock(return_value=[XmlAttr(('name', name))])
        context = {'styles': InheritedDict()}
        style = Style(xml_node, context)

        parse_attrs(style)

        msg = '"name" attribute value should be used as style name'
        self.assertEqual(name, style.name, msg)

    @case([('bg', '#000')])
    @case([('name', ''), ('bg', '#000')])
    @case([('name', None), ('bg', '#000')])
    def test_parse_attrs_raise_if_name_empty_or_not_exist(self, attrs):
        xml_node = Mock()
        xml_node.get_attrs = Mock(return_value=[XmlAttr(attr) for attr in attrs])
        context = {'styles': InheritedDict()}
        style = Style(xml_node, context)

        msg = '"name" attribute value should be used as style name'
        with self.assertRaises(Exception, msg=msg):
            parse_attrs(style)

class ApplyTest(TestCase):
    @case('one,two', ['one', 'two'], ['one', 'two', 'three'])
    @case('one , two', ['one', 'two'], ['one', 'two', 'three'])
    @case(['one', 'two'], ['one', 'two'], ['one', 'two', 'three'])
    def test_apply_styles(self, styles_to_apply, styles_applied, all_styles):
        context = {'styles': InheritedDict()}
        for key in all_styles:
            context['styles'][key] = [Mock() for i in range(0, 5)]
        node = Mock()
        node.context = context

        apply_styles(node, styles_to_apply)

        msg = 'style items should be applied to node from passed styles'
        self.assertTrue(self._styles_applied(node, context['styles'], styles_applied), msg)

    def _styles_applied(self, node, styles, keys):
        styles = styles.to_dictionary()

        for key, style_items in styles.items():
            for item in style_items:
                if key in keys and item.apply.call_args != call(node):
                    return False
                if key not in keys and item.apply.called:
                    return False

        return True

if __name__ == '__main__':
    main()
