from importlib import import_module
from common.reflection.execution import run

class Command:
    def __init__(self, caller, call):
        self._caller = caller
        self._call = call

    def run(self, method_locals):
        caller = self._caller
        try:
            module = import_module(self._caller)
            caller = 'module'
            method_locals['module'] = module
        except ImportError:
            pass
        run(caller + '.' + self._call, method_locals)
