'''Contains logic for Code node'''

from sys import exc_info
from textwrap import dedent
from traceback import extract_tb
from pyviews.core.node import Node
from pyviews.core.compilation import CompilationError
from pyviews.rendering.setup import NodeSetup

class Code(Node):
    '''Wrapper under python code inside view'''
    def __init__(self, xml_node):
        super().__init__(xml_node)

def get_code_setup():
    '''Creates node setup for Code'''
    return NodeSetup(render_steps=[run_code])

def run_code(node: Code, parent_node: Node = None):
    '''Executes node content as python module and adds its definitions to globals'''
    if not node.xml_node.text:
        return
    code = node.xml_node.text
    try:
        globs = parent_node.globals.to_dictionary()
        exec(dedent(code), globs)
        definitions = [(key, value) for key, value in globs.items() \
                    if key != '__builtins__' and not parent_node.globals.has_key(key)]
        for key, value in definitions:
            parent_node.globals[key] = value
    except SyntaxError as err:
        error = _get_compilation_error(code, 'Invalid syntax', err, err.lineno)
        raise error from err
    except:
        info = exc_info()
        cause = info[1]
        line_number = extract_tb(info[2])[-1][1]
        error = _get_compilation_error(code, 'Code execution is failed', cause, line_number)
        raise error from cause

def _get_compilation_error(code, title, cause, line_number):
    msg = '{0}:\n{1}'.format(title, code)
    error = CompilationError(msg, str(cause))
    error.add_cause(cause)
    error.add_info('Line number', line_number)
    return error