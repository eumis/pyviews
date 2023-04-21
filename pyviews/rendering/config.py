"""Rendering setup"""

from os.path import abspath

from injectool import add_singleton


def use_rendering():
    """setup rendering dependencies"""
    add_singleton('views_folder', abspath('views'))
    add_singleton('view_ext', 'xml')
