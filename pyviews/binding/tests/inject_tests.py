from unittest.mock import Mock, call

from injectool import add_singleton, use_container

from pyviews.binding.binder import BindingContext
from pyviews.binding.inject import inject_binding
from pyviews.core.rendering import Node
from pyviews.core.xml import XmlAttr


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
    }) # yapf: disable

    with use_container():
        dependency = Mock()
        add_singleton(key, dependency)
        inject_binding(context)

        assert setter.call_args == call(node, xml_attr.name, dependency)
