"""Binding setup"""

from typing import Optional
from injectool import add_singleton

from pyviews.binding.binder import Binder
from pyviews.binding.expression import bind_setter_to_expression
from pyviews.binding.inject import inject_binding
from pyviews.binding.inline import bind_inline
from pyviews.binding.once import run_once


def use_binding(binder: Optional[Binder] = None):
    """setup binder and default bindings"""
    binder = binder if binder else Binder()
    add_singleton(Binder, binder)
    binder.add_rule('once', run_once)
    binder.add_rule('oneway', bind_setter_to_expression)
    binder.add_rule('inline', bind_inline)
    binder.add_rule('inject', inject_binding)
