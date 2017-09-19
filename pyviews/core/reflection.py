from importlib import import_module

def create_inst(module_name, class_name, args=None, kwargs=None):
    args = [] if args is None else args
    kwargs = {} if kwargs is None else kwargs
    try:
        module = import_module(module_name)
    except Exception as ex:
        raise ImportError(ex)
    class_ = getattr(module, class_name)
    return class_(*args, **kwargs)

def import_path(path):
    if path is None:
        return None
    try:
        return import_module(path)
    except ImportError:
        pass
    (path, name) = split_by_last_dot(path)
    module = import_path(path)
    return module.__dict__[name] if module else None

def split_by_last_dot(expr):
    last_dot = expr.rfind('.')
    if last_dot == -1:
        return('', expr)
    return (expr[:last_dot], expr[last_dot+1:])

# from inspect import getfullargspec
# from pyviews.core.ioc import inject
# @inject('event_key')
# def get_event_handler(command, event_key='event'):
#     spec = getfullargspec(command)
#     arg = spec[0][0] if spec[0] else ''
#     if arg == event_key:
#         return lambda e, com=command: com(e)
#     return lambda e, com=command: com()
