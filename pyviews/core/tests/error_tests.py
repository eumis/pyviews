from os import linesep
from typing import List

from pytest import mark

from pyviews.core import PyViewsError, ViewInfo


def _concat(*items):
    items = [item.strip(linesep) for item in items]
    return linesep + linesep.join(items) + linesep


class CoreErrorTests:
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
