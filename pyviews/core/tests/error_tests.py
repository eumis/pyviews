from os import linesep
from unittest.mock import Mock, call

from pytest import fail

from pyviews.core import PyViewsError, ViewInfo, error_handling


class TestError(PyViewsError):
    def __init__(self, message=None, view_info=None):
        super().__init__(message=message, view_info=view_info)


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
    def test_empty_output():
        error = TestError()

        expected = f'{linesep}' \
                   f'Info ------------------------------------------------------------------------------------------------{linesep}' \
                   f'{linesep}' \
                   f'TestError -------------------------------------------------------------------------------------------{linesep}' \
                   f'{linesep}' \
                   f'View info -------------------------------------------------------------------------------------------'
        assert str(error) == expected


class ErrorHandlingTests:
    """error_handling_tests"""

    @staticmethod
    def test_raises_passed_error():
        """should handle errors and raise passed error"""
        error = PyViewsError('test message')
        try:
            with error_handling(error):
                raise ValueError('test value error')
        except PyViewsError as actual:
            assert actual == error
        except BaseException:
            fail()

    @staticmethod
    def test_raises_error_of_passed_type():
        """should handle errors and raise passed error"""
        error_type = TestError
        try:
            with error_handling(TestError):
                raise ValueError('test value error')
        except PyViewsError as actual:
            assert isinstance(actual, error_type)
        except BaseException:
            fail()

    @staticmethod
    def test_adds_info_to_error():
        """should add info to PyViewsError"""
        add_info_callback = Mock()
        error = PyViewsError('test message')
        try:
            with error_handling(error, add_info_callback):
                raise ValueError('test value error')
        except PyViewsError:
            assert add_info_callback.call_args == call(error)
        except BaseException:
            fail()

    @staticmethod
    def test_reraises_pyviews_error():
        """should handle PyViewsError, add info and reraise"""
        add_info_callback = Mock()
        error = PyViewsError('new error')
        handled_error = PyViewsError('handled error')
        try:
            with error_handling(error, add_info_callback):
                raise handled_error
        except PyViewsError as actual:
            assert actual == handled_error
            assert add_info_callback.call_args == call(handled_error)
        except BaseException:
            fail()
