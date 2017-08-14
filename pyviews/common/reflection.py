from importlib import import_module
from inspect import getfullargspec
from pyviews.common.settings import EVENT_KEY

def create_inst(module_name, class_name, *args):
    module = import_module(module_name)
    class_ = getattr(module, class_name)
    return class_(*args)

def run(code, run_globals, run_locals):
    return eval(code, run_globals, run_locals)

def get_handler(command):
    spec = getfullargspec(command)
    arg = spec[0][0] if spec[0] else ''
    if arg == EVENT_KEY:
        return lambda e, com=command: com(e)
    return lambda e, com=command: com()
