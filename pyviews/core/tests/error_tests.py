from os import linesep
from typing import List
from unittest.mock import Mock, call

from pytest import mark, fail

from pyviews.core import PyViewsError, ViewInfo, error_handling


def _concat(*items):
    items = [item.strip(linesep) for item in items]
    return linesep + linesep.join(items) + linesep


class PyViewsErrorTests:
    @staticmethod
    @mark.parametrize('message, view_info, error_output', [
        ('', None, _concat('Message: ')),
        ('', ViewInfo('view name', 25), _concat(
            'Message: ',
            'View info: Line 25 in "view name"'
        )),
        ('some error message', None, _concat('Message: some error message')),
        ('some error message', ViewInfo('view', 1), _concat(
            'Message: some error message',
            'View info: Line 1 in "view"'
        ))
    ])
    def test_init(message, view_info: ViewInfo, error_output):
        """__init__() should setup message and view info"""
        error = PyViewsError(message, view_info)

        assert str(error) == error_output

    @staticmethod
    @mark.parametrize('view_infos, view_output', [
        ([ViewInfo('view name', 25)],
         _concat('View info: Line 25 in "view name"')),
        ([ViewInfo('view name', 25), ViewInfo('view name', 25)],
         _concat('View info: Line 25 in "view name"')),
        ([ViewInfo('view name', 25), ViewInfo('view name', 30)],
         _concat('View info: Line 25 in "view name"')),
        ([ViewInfo('view name', 25), ViewInfo('parent view name', 9)],
         _concat('View info: Line 25 in "view name"',
                 '\tView info: Line 9 in "parent view name"')),
        ([ViewInfo('view name', 25), ViewInfo('parent view name', 9), ViewInfo('root', 10)],
         _concat('View info: Line 25 in "view name"',
                 '\tView info: Line 9 in "parent view name"',
                 '\t\tView info: Line 10 in "root"')),
    ])
    def test_add_view_info(view_infos: List[ViewInfo], view_output: str):
        """add_view_info() should add view info line to error output"""
        error = PyViewsError('')
        expected = _concat('Message: ', view_output)

        for info in view_infos:
            error.add_view_info(info)

        assert str(error) == expected

    @staticmethod
    @mark.parametrize('header, message, info_output', [
        ('', 'message', ': message'),
        ('header', '', 'header: '),
        ('header', 'message', 'header: message')
    ])
    def test_add_info(header, message, info_output: str):
        """add_info() should add info line to error output"""
        error = PyViewsError('')
        expected = _concat('Message: ', info_output)

        error.add_info(header, message)

        assert str(error) == expected

    @staticmethod
    @mark.parametrize('cause_error, cause_output', [
        (ValueError('any value error'), 'Cause error: ValueError - any value error'),
        (TypeError('type error message'), 'Cause error: TypeError - type error message')
    ])
    def test_add_cause(cause_error: Exception, cause_output: str):
        """add_cause() should add info about cause error"""
        error = PyViewsError('')
        expected = _concat('Message: ', cause_output)

        error.add_cause(cause_error)

        assert str(error) == expected


class TestError(PyViewsError):
    def __init__(self):
        super().__init__('message')


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
