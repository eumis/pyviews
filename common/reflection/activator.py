from importlib import import_module

def create_inst(module_name, class_name, *args):
    module = import_module(module_name)
    class_ = getattr(module, class_name)
    return class_(*args)
