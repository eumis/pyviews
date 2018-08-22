'''Module contains Code node'''

from sys import exc_info
from importlib import import_module
from inspect import signature, Parameter
from textwrap import dedent
from traceback import extract_tb
from typing import Tuple, List, Dict
from pyviews.core.node import Node, InstanceNode
from pyviews.core.xml import XmlNode
from pyviews.core.compilation import CompilationError
from pyviews.core.observable import InheritedDict
from pyviews.rendering import RenderingError

class Code(Node):
    '''Wrapper under python code inside view'''
    def __init__(self, parent_node, xml_node, parent_context=None):
        super().__init__(xml_node, parent_context)
        self._parent_globals = parent_node.globals
        self.text = ''

    def render_children(self):
        '''Executes node content as python module and adds its definitions to globals'''
        try:
            globs = self._parent_globals.to_dictionary()
            exec(dedent(self.text), globs)
            definitions = [(key, value) for key, value in globs.items() \
                        if key != '__builtins__' and not self._parent_globals.has_key(key)]
            for key, value in definitions:
                self._parent_globals[key] = value
        except SyntaxError as err:
            error = self._get_compilation_error('Invalid syntax', err, err.lineno)
            raise error from err
        except:
            info = exc_info()
            cause = info[1]
            line_number = extract_tb(info[2])[-1][1]
            error = self._get_compilation_error('Code execution is failed', cause, line_number)
            raise error from cause

    def _get_compilation_error(self, title, cause, line_number):
        msg = '{0}:\n{1}'.format(title, self.text)
        error = CompilationError(msg, str(cause))
        error.add_cause(cause)
        error.add_info('Line number', line_number)
        return error

def create_node(xml_node: XmlNode, **init_args):
    '''Creates node from xml node using namespace as module and tag name as class name'''
    inst_type = _get_inst_type(xml_node)
    init_args['xml_node'] = xml_node
    inst = create_inst(inst_type, **init_args)
    if not isinstance(inst, Node):
        inst = convert_to_node(inst, **init_args)
    return inst

def _get_inst_type(xml_node: XmlNode):
    (module_path, class_name) = (xml_node.namespace, xml_node.name)
    try:
        return import_module(module_path).__dict__[class_name]
    except (KeyError, ImportError, ModuleNotFoundError):
        message = 'Import "{0}.{1}" is failed.'.format(module_path, class_name)
        raise RenderingError(message, xml_node.view_info)

def create_inst(inst_type, **init_args):
    '''Creates class instance with args'''
    args, kwargs = get_init_args(inst_type, **init_args)
    return inst_type(*args, **kwargs)

def get_init_args(inst_type, **init_args) -> Tuple[List, Dict]:
    '''Returns tuple with args and kwargs to pass it to inst_type constructor'''
    try:
        parameters = signature(inst_type).parameters.values()
        args = [init_args[p.name] for p in parameters if p.default == Parameter.empty]
        kwargs = {p.name: init_args[p.name] for p in parameters \
                    if p.default != Parameter.empty and p.name in init_args}
    except KeyError as key_error:
        msg_format = 'parameter with key "{0}" is not found in node args'
        raise RenderingError(msg_format.format(key_error.args[0]))
    return (args, kwargs)

def convert_to_node(instance, xml_node: XmlNode, node_globals: InheritedDict = None) -> InstanceNode:
    '''Wraps passed instance with InstanceNode'''
    return InstanceNode(instance, xml_node, node_globals)
