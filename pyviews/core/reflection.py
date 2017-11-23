from importlib import import_module

def import_path(path):
    try:
        return import_module(path)
    except ImportError:
        return _import_module_entry(path)
    except:
        raise ImportError(path)

def _import_module_entry(path):
    (module, name) = split_by_last_dot(path)
    try:
        module = import_module(module)
        return module.__dict__[name]
    except:
        raise ImportError(path)

def split_by_last_dot(expr):
    last_dot = expr.rfind('.')
    if last_dot == -1:
        return(expr, None)
    return (expr[:last_dot], expr[last_dot+1:])
