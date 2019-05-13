import unittest
from unittest import TestCase
from importlib import import_module

import pytest
from pytest import mark, raises

from pyviews.core.reflection import import_path


@mark.parametrize('path, expected', [
    ('pytest', pytest),
    ('unittest', unittest),
    ('unittest.TestCase', TestCase),
    ('importlib.import_module', import_module)
])
def test_import_path(path, expected):
    """import_path() should import module"""
    assert import_path(path) == expected


@mark.parametrize('invalid_path', [
    None,
    '',
    '    ',
    'asdf',
    'unittest.asdf',
])
def test_import_path_raises(invalid_path):
    """import_path() should raise ImportError"""
    with raises(ImportError):
        import_path(invalid_path)
