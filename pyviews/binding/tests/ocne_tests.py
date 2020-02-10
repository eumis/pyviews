from unittest.mock import Mock, call

from pytest import mark

from pyviews.binding import BindingContext
from pyviews.binding.once import run_once
from pyviews.core import InheritedDict, XmlAttr


@mark.parametrize('expr_body, node_globals, expected_value', [
    ('1+1', {}, 2),
    ('val', {'val': 2}, 2),
    ('val + 1', {'val': 2}, 3)
])
def test_run_once(expr_body: str, node_globals: dict, expected_value):
    """run_once() should call passed modifier"""
    node = Mock(node_globals=InheritedDict(node_globals))
    modifier, xml_attr = Mock(), XmlAttr('name')

    run_once(BindingContext({
        'node': node,
        'expression_body': expr_body,
        'modifier': modifier,
        'xml_attr': xml_attr
    }))

    assert modifier.call_args == call(node, xml_attr.name, expected_value)
