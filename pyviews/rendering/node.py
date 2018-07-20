'''Module contains Code node'''

from sys import exc_info
from textwrap import dedent
from traceback import extract_tb
from pyviews.core.node import Node
from pyviews.core.compilation import CompilationError

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
