"""Common core functionality"""

from contextlib import contextmanager
from os import linesep
from collections import namedtuple
from sys import exc_info
from typing import Callable, Union, Type, Generator, List, Any

ViewInfo = namedtuple('ViewInfo', ['view', 'line'])


class PyViewsError(Exception):
    """Base error class for custom exceptions"""

    def __init__(self, message: str = '', view_info: ViewInfo = None):
        super().__init__(linesep)
        self.infos: List[str] = []
        self.view_infos: List[ViewInfo] = []
        # noinspection PyTypeChecker
        self.cause_error: BaseException = None
        self.message = message
        if view_info:
            self.add_view_info(view_info)

    def add_info(self, header: str, message: Any):
        """Adds "header: message" line to error message"""
        try:
            next(info for info in self.infos if info.startswith(header))
        except StopIteration:
            self.infos.append(self._format_info(header, str(message)))

    @staticmethod
    def _format_info(header: str, message: str):
        return f'{header}: {message}'

    def add_view_info(self, view_info: ViewInfo):
        """Adds view information to error message"""
        try:
            next(info for info in self.view_infos if info.view == view_info.view)
        except StopIteration:
            self.view_infos.insert(0, view_info)

    def __str__(self) -> str:
        self.args = (linesep.join(self._get_messages()),) + self.args[1:]
        return super().__str__()

    def _get_messages(self) -> Generator[str, None, None]:
        yield from self._get_info()
        yield from self._get_error()
        yield from self._get_view_info()

    def _get_info(self) -> Generator[str, None, None]:
        yield self._get_separator('Info')
        yield from self.infos

    def _get_error(self) -> Generator[str, None, None]:
        yield self._get_separator(self.__class__.__name__)
        if self.cause_error:
            yield self._format_info('Cause error',
                                    f'{type(self.cause_error).__name__} - {self.cause_error}')
        if self.message:
            yield self._format_info('Message', self.message)

    def _get_view_info(self) -> Generator[str, None, None]:
        yield self._get_separator('View info')
        for i, view_info in enumerate(self.view_infos):
            yield '{0}Line {1} in "{2}"'.format(i * '\t', view_info.line, view_info.view)

    @staticmethod
    def _get_separator(title: str):
        count = 100 - len(title)
        return f'{linesep}{title} {count * "-"}'


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
        error_to_raise.cause_error = info[1]
        raise error_to_raise from info[1]


def _do_nothing(_):
    pass
