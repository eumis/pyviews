from importlib import import_module

def import_path(path):
    if not path:
        raise ImportError(path)
    try:
        return import_module(path)
    except ImportError:
        pass
    try:
        (module_path, name) = split_by_last_dot(path)
        if name is None:
            raise ImportError
        module = import_path(module_path)
        if name not in module.__dict__:
            raise ImportError
        return module.__dict__[name]
    except ImportError:
        raise ImportError(path)

def split_by_last_dot(expr):
    last_dot = expr.rfind('.')
    if last_dot == -1:
        return(expr, None)
    return (expr[:last_dot], expr[last_dot+1:])
