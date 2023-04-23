"""Import in runtime by fullname"""

from importlib import import_module
from typing import Any, Tuple


def import_path(path: str) -> Any:
    """Imports module, class, function by full name"""
    try:
        return import_module(path)
    except ImportError:
        return _import_module_entry(path)
    except BaseException as exc:
        raise ImportError(path) from exc


def _import_module_entry(path: str) -> Any:
    (module, name) = _split_by_last_dot(path)
    try:
        module = import_module(module)
        return module.__dict__[name]
    except BaseException as exc:
        raise ImportError(path) from exc


def _split_by_last_dot(expr: str) -> Tuple[str, str]:
    last_dot = expr.rfind('.')
    if last_dot == -1:
        return expr, ''
    return expr[:last_dot], expr[last_dot + 1:]
