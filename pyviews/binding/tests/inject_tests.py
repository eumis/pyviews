from unittest.mock import Mock, call

from injectool import use_container, add_singleton
from pyviews.binding import BindingContext
from pyviews.binding.inject import inject_binding
from pyviews.core import Node, XmlAttr


def test_inject_binding():
    """should set resolved dependency"""
    key = 'key'
    node = Node(Mock())
    xml_attr = XmlAttr('name')
    setter = Mock()
    context = BindingContext({
        'node': node,
        'expression_body': '"key"',
        'xml_attr': xml_attr,
        'setter': setter
    })

    with use_container():
        dependency = Mock()
        add_singleton(key, dependency)
        inject_binding(context)

        assert setter.call_args == call(node, xml_attr.name, dependency)
