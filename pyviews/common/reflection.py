from importlib import import_module
from inspect import getfullargspec
from pyviews.common.ioc import inject

def create_inst(module_name, class_name, *args):
    module = import_module(module_name)
    class_ = getattr(module, class_name)
    return class_(*args)

@inject('event_key')
def get_handler(command, event_key='event'):
    spec = getfullargspec(command)
    arg = spec[0][0] if spec[0] else ''
    if arg == event_key:
        return lambda e, com=command: com(e)
    return lambda e, com=command: com()
