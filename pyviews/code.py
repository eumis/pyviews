"""Contains logic for Code node"""

from sys import exc_info
from textwrap import dedent
from traceback import extract_tb
from pyviews.core import Node, InheritedDict, CompilationError


class Code(Node):
    """Wrapper under python code inside view"""

    def __init__(self, xml_node):
        super().__init__(xml_node)


def run_code(node: Code,
             parent_node: Node = None,
             node_globals: InheritedDict = None,
             **_):
    """Executes node content as python module and adds its definitions to globals"""
    if not node.xml_node.text:
        return
    code = node.xml_node.text
    try:
        globs = node_globals.to_dictionary()
        exec(dedent(code), globs)
        definitions = [(key, value) for key, value in globs.items()
                       if key != '__builtins__' and key not in node_globals]
        for key, value in definitions:
            parent_node.node_globals[key] = value
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
