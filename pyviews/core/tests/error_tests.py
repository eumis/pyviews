from os import linesep
from unittest.mock import Mock, call

from pytest import fixture, mark, raises

from pyviews.core.error import PyViewsError, ViewInfo, error_handling


class TestError(PyViewsError):

    def __init__(self, message = None, view_info = None):
        super().__init__(message = message, view_info = view_info)


class PyViewsErrorTests:

    @staticmethod
    def test_error_output():
        error = TestError()
        error.message = 'message text'
        error.cause_error = ImportError('module.function')

        error.add_view_info(ViewInfo('most inner view', 23))
        error.add_view_info(ViewInfo('inner view', 9))
        error.add_view_info(ViewInfo('app', 17))

        error.add_info('Info', 'info message')
        error.add_info('Other info', 'other info message')

        expected = f'{linesep}' \
                   f'Info ------------------------------------------------------------------------------------------------{linesep}' \
                   f'Info: info message{linesep}' \
                   f'Other info: other info message{linesep}' \
                   f'{linesep}' \
                   f'TestError -------------------------------------------------------------------------------------------{linesep}' \
                   f'Cause error: ImportError - module.function{linesep}' \
                   f'Message: message text{linesep}' \
                   f'{linesep}' \
                   f'View info -------------------------------------------------------------------------------------------{linesep}' \
                   f'Line 17 in "app"{linesep}' \
                   f'\tLine 9 in "inner view"{linesep}' \
                   f'\t\tLine 23 in "most inner view"'
        assert str(error) == expected

    @staticmethod
    def test_same_info_output():
        error = TestError()

        error.add_info('Info', 'info message')
        error.add_info('Info', 'info message')

        error.add_info('Event', 'some event')
        error.add_info('Event', 'other event')

        obj1, obj2 = object(), object()
        error.add_info('Object', obj1)
        error.add_info('Object', obj2)

        expected = f'{linesep}' \
                   f'Info ------------------------------------------------------------------------------------------------{linesep}' \
                   f'Info: info message{linesep}' \
                   f'Event: some event{linesep}' \
                   f'Object: {obj1}{linesep}' \
                   f'{linesep}' \
                   f'TestError -------------------------------------------------------------------------------------------{linesep}' \
                   f'{linesep}' \
                   f'View info -------------------------------------------------------------------------------------------'
        assert str(error) == expected

    @staticmethod
    def test_empty_output():
        error = TestError()

        expected = f'{linesep}' \
                   f'Info ------------------------------------------------------------------------------------------------{linesep}' \
                   f'{linesep}' \
                   f'TestError -------------------------------------------------------------------------------------------{linesep}' \
                   f'{linesep}' \
                   f'View info -------------------------------------------------------------------------------------------'
        assert str(error) == expected


@fixture
def error_fixture(request):
    request.cls.error = PyViewsError('test error')
    request.cls.add_error_info = Mock()


@mark.usefixtures('error_fixture')
class ErrorHandlingTests:
    """error_handling_tests"""

    error: PyViewsError
    add_error_info: Mock

    def test_raises_passed_error(self):
        """should handle errors and raise passed error"""
        with raises(PyViewsError) as actual:
            with error_handling(self.error):
                raise ValueError('test value error')

        assert actual.value == self.error

    @staticmethod
    def test_raises_error_of_passed_type():
        """should handle errors and raise passed error"""
        with raises(TestError):
            with error_handling(TestError):
                raise ValueError('test value error')

    def test_adds_info_to_error(self):
        """should add info to PyViewsError"""
        with raises(PyViewsError):
            with error_handling(self.error, self.add_error_info):
                raise ValueError('test value error')

        assert self.add_error_info.call_args == call(self.error)

    def test_reraises_pyviews_error(self):
        """should handle PyViewsError, add info and reraise"""
        handled_error = PyViewsError('handled error')
        with raises(PyViewsError) as actual:
            with error_handling(self.error, self.add_error_info):
                raise handled_error
        actual_error = actual.value

        assert actual_error == handled_error
        assert self.add_error_info.call_args == call(handled_error)
