"""Binding setup"""

from injectool import add_singleton

from pyviews.binding.binder import Binder
from pyviews.binding.once import run_once
from pyviews.binding.expression import bind_setter_to_expression
from pyviews.binding.inline import bind_inline


def use_binding(binder: Binder = None):
    """setup binder and default bindings"""
    binder = binder if binder else Binder()
    binder.add_rule('once', run_once)
    binder.add_rule('oneway', bind_setter_to_expression)
    binder.add_rule('inline', bind_inline)
    add_singleton(Binder, binder)
