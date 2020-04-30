from injectool import add_singleton

from pyviews.binding import Binder, run_once, bind_setter_to_expression, bind_inline


def use_binding(binder: Binder = None):
    """setup binder and default bindings"""
    binder = binder if binder else Binder()
    binder.add_rule('once', run_once)
    binder.add_rule('oneway', bind_setter_to_expression)
    binder.add_rule('inline', bind_inline)
    add_singleton(Binder, binder)
