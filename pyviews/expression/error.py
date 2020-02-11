"""Expression errors"""

from pyviews.core import PyViewsError


class ExpressionError(PyViewsError):
    """Error for failed expression"""

    def __init__(self, message, expression: str = None):
        super().__init__(message)
        self.expression: str = expression
        if expression:
            self.add_expression_info(expression)

    def add_expression_info(self, expression: str):
        """Adds info about expression to error"""
        self.expression = expression
        self.add_info('Expression', expression)
