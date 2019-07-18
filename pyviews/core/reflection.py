"""Import in runtime by fullname"""

from importlib import import_module


def import_path(path):
    """Imports module, class, function by full name"""
    try:
        return import_module(path)
    except ImportError:
        return _import_module_entry(path)
    except Exception as error:
        raise ImportError(path) from error


def _import_module_entry(path):
    (module, name) = _split_by_last_dot(path)
    try:
        module = import_module(module)
        return module.__dict__[name]
    except Exception as error:
        raise ImportError(path) from error


def _split_by_last_dot(expr):
    last_dot = expr.rfind('.')
    if last_dot == -1:
        return expr, None
    return expr[:last_dot], expr[last_dot + 1:]
