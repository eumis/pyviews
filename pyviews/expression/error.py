from pyviews.core import PyViewsError


class ExpressionError(PyViewsError):
    """Error for failed expression"""

    def __init__(self, message, expression: str):
        super().__init__(message)
        self.expression: str = expression
        self.add_info('Expression', expression)
