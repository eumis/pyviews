from unittest import TestCase, main
from unittest.mock import Mock, call, patch
from tests.utility import case
from pyviews.tk.widgets import WidgetNode
from pyviews.tk import modifiers
from pyviews.tk.modifiers import bind, bind_all, set_attr, config, visible

class TkModifiersTests(TestCase):
    def setUp(self):
        self.node = Mock()
        self._apply_styles = modifiers.apply_styles
        modifiers.apply_styles = Mock() 

    def test_bind(self):
        event = 'event'
        command = lambda: None

        bind(self.node, event, command)

        self.assertEqual(self.node.bind.call_args, call(event, command))

    def test_bind_all(self):
        event = 'event'
        command = lambda: None

        bind_all(self.node, event, command)

        self.assertEqual(self.node.bind_all.call_args, call(event, command))

    def test_set_attr_style(self):
        key = 'style'
        value = 2

        set_attr(self.node, key, value)

        self.assertEqual(modifiers.apply_styles.call_args, call(self.node, value))

    def test_set_attr(self):
        key = 'key'
        value = 2

        set_attr(self.node, key, value)

        self.assertEqual(self.node.set_attr.call_args, call(key, value))

    def test_config(self):
        key = 'key'
        value = 2

        config(self.node, key, value)

        self.assertEqual(self.node.widget.config.call_args, call(**{key: value}))

    def test_visible_true(self):
        visible(self.node, None, True)

        self.assertEqual(self.node.geometry.apply.call_args, call(self.node.widget))

    def test_visible_false(self):
        visible(self.node, None, False)

        self.assertEqual(self.node.geometry.forget.call_args, call(self.node.widget))

    def tearDown(self):
        modifiers.apply_styles = self._apply_styles

if __name__ == '__main__':
    main()
