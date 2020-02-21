from unittest.mock import Mock, call

from pytest import mark, raises, fixture

from pyviews.core import BindingError, Node, XmlAttr, Binding
from pyviews.binding.binder import Binder, BindingContext

BINDING_TYPE = 'default_binding_type'


@fixture
def binding_context_fixture(request):
    request.cls.context = BindingContext()


@mark.usefixtures('binding_context_fixture')
class BindingContextTests:
    """BindingContext tests"""

    def test_node(self):
        """node property should use key 'node'"""
        value = Node(Mock())
        init_value = self.context.node

        self.context.node = value

        assert init_value is None
        assert self.context.node == value
        assert self.context['node'] == value

    def test_expression_body(self):
        """expression_body property should use key 'expression_body'"""
        value = "1 + 1"
        init_value = self.context.expression_body

        self.context.expression_body = value

        assert init_value is None
        assert self.context.expression_body == value
        assert self.context['expression_body'] == value

    def test_setter(self):
        """setter should use key 'setter'"""

        def value(_, __, ___):
            pass

        init_value = self.context.setter

        self.context.setter = value

        assert init_value is None
        assert self.context.setter == value
        assert self.context['setter'] == value

    def test_xml_attr(self):
        """xml_attr property should use key 'xml_attr'"""
        value = XmlAttr('name')
        init_value = self.context.xml_attr

        self.context.xml_attr = value

        assert init_value is None
        assert self.context.xml_attr == value
        assert self.context['xml_attr'] == value


class TestRule:
    def __init__(self, suitable: bool, binding: Binding = None):
        self._suitable = suitable
        self.suitable_args = None
        self.apply_args = None
        self.binding = binding

    def suitable(self, context: BindingContext):
        self.suitable_args = context
        return self._suitable

    def bind(self, context: BindingContext):
        self.apply_args = context
        return self.binding


def _find_suitable_rule(rules):
    try:
        expected = next(rule for rule in reversed(rules) if rule.suitable())
    except StopIteration:
        expected = None
    return expected


def _create_binder(binding_type, rules):
    binder = Binder()
    for rule in rules:
        binder.add_rule(binding_type, rule.bind, rule.suitable)
    return binder


_binding_args = [
    {},
    {'node': Mock()},
    {'node': Mock(), 'setter': lambda *args: None}
]


class BinderTests:
    """Binder tests"""

    @staticmethod
    def test_raises_if_rule_not_found():
        """apply() should raise error if rule is not found"""
        binder = Binder()

        with raises(BindingError):
            binder.bind('some_type', BindingContext())

    @staticmethod
    @mark.parametrize('rules, rule_index', [
        [[TestRule(True), TestRule(True)], 1],
        [[TestRule(False), TestRule(True)], 1],
        [[TestRule(True), TestRule(False)], 0]
    ])
    def test_bind_by_rule(rules, rule_index):
        """apply() should call bind() for found rule"""
        binder = _create_binder(BINDING_TYPE, rules)
        expected = rules[rule_index]
        context = BindingContext({'node': Mock(), 'setter': lambda *args: None})

        binder.bind(BINDING_TYPE, context)

        assert expected.apply_args == context

    @staticmethod
    @mark.parametrize('binding', [None, Mock()])
    def test_adds_binding_to_node(binding):
        """apply() should add binding to node"""
        binder = _create_binder(BINDING_TYPE, [TestRule(True, binding)])
        node = Mock()

        binder.bind(BINDING_TYPE, BindingContext({'node': node}))

        expected_call = call(binding) if binding else None
        assert node.add_binding.call_args == expected_call
