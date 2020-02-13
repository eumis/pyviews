"""Compilation implementation"""

from .error import ExpressionError
from .expression import Expression, ObjectNode, execute
from .parsing import is_expression, parse_expression
