"""Common core functionality"""

from contextlib import contextmanager
from os import linesep
from collections import namedtuple
from sys import exc_info
from typing import Callable, Union, Type

ViewInfo = namedtuple('ViewInfo', ['view', 'line'])


class PyViewsError(Exception):
    """Base error class for custom exceptions"""

    def __init__(self, message: str, view_info: ViewInfo = None):
        super().__init__(linesep)
        self._view_infos = []
        self.message = message
        self.add_info('Message', message)
        if view_info:
            self.add_view_info(view_info)

    def add_view_info(self, view_info: ViewInfo):
        """Adds view information to error message"""
        try:
            next(info for info in self._view_infos if info.view == view_info.view)
        except StopIteration:
            indent = len(self._view_infos) * '\t'
            self._view_infos.append(view_info)
            info = 'Line {0} in "{1}"'.format(view_info.line, view_info.view)
            self.add_info(indent + 'View info', info)

    def add_info(self, header, message):
        """Adds "header: message" line to error message"""
        current_message = self.args[0]
        message = current_message + self._format_info(header, message)
        self.args = (message,) + self.args[1:]

    @staticmethod
    def _format_info(header, message):
        return '{0}: {1}{2}'.format(header, message, linesep)

    def add_cause(self, error: BaseException):
        """Adds cause error to error message"""
        self.add_info('Cause error', '{0} - {1}'.format(type(error).__name__, error))


@contextmanager
def error_handling(error_to_raise: Union[PyViewsError, Type[PyViewsError]],
                   add_error_info: Callable[[PyViewsError], None] = None):
    """handles error and raises PyViewsError with custom error info"""
    add_error_info = add_error_info if add_error_info is not None else _do_nothing
    try:
        yield
    except PyViewsError as error:
        add_error_info(error)
        raise
    except BaseException:
        info = exc_info()
        if not isinstance(error_to_raise, PyViewsError):
            error_to_raise = error_to_raise()
        add_error_info(error_to_raise)
        error_to_raise.add_cause(info[1])
        raise error_to_raise from info[1]


def _do_nothing(_):
    pass
