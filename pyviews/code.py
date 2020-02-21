"""Contains logic for Code node"""

from sys import exc_info
from textwrap import dedent
from traceback import extract_tb
from pyviews.core import Node, XmlNode, ViewInfo
from pyviews.expression import ExpressionError
from pyviews.rendering.common import RenderingContext


class Code(Node):
    """Wrapper under python code inside view"""

    def __init__(self, xml_node):
        super().__init__(xml_node)


def run_code(node: Code, context: RenderingContext):
    """Rendering step: executes node content as python module and adds its definitions to globals"""
    if not node.xml_node.text:
        return
    code = node.xml_node.text
    try:
        globs = context.node_globals.to_dictionary()
        exec(dedent(code), globs)
        _update_context(globs, context)
    except SyntaxError as err:
        error = _get_error(node.xml_node, err, err.lineno)
        raise error from err
    except BaseException:
        info = exc_info()
        cause, line_number = info[1], extract_tb(info[2])[-1][1]
        error = _get_error(node.xml_node, cause, line_number)
        raise error from cause


def _update_context(globs: dict, context: RenderingContext):
    definitions = [(key, value) for key, value in globs.items()
                   if key != '__builtins__' and key not in context.node_globals]
    for key, value in definitions:
        context.parent_node.node_globals[key] = value


def _get_error(xml_node: XmlNode, cause: BaseException, line_number: int) -> ExpressionError:
    error = ExpressionError()
    error.cause_error = cause
    error.add_view_info(ViewInfo('<Code>', line_number))
    error.add_view_info(xml_node.view_info)
    return error
