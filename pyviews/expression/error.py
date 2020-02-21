"""Expression errors"""

from pyviews.core import PyViewsError


class ExpressionError(PyViewsError):
    """Error for failed expression"""

    def __init__(self, message=None, expression_body: str = None):
        super().__init__(message=message)
        self.expression: str = expression_body
        if expression_body:
            self.add_expression_info(expression_body)

    def add_expression_info(self, expression: str):
        """Adds info about expression to error"""
        self.expression = expression
        self.add_info('Expression', expression)
