from importlib import import_module

def create(module_name, class_name):
    module = import_module(module_name)
    class_ = getattr(module, class_name)
    return class_()
