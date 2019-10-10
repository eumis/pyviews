"""pypi package setup"""

import codecs
import re
from os.path import join as join_path, dirname
from setuptools import setup, find_packages


def setup_package():
    """Package setup"""
    setup(
        name='pyviews',
        version=_get_version(),
        description='Base package for xml views',
        long_description=_get_long_description(),
        long_description_content_type='text/markdown',
        url='https://github.com/eumis/pyviews',
        author='eumis(Eugen Misievich)',
        author_email='misievich@gmail.com',
        license='MIT',
        classifiers=[
            #   2 - Pre-Alpha
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.6'
        ],
        python_requires='>=3.6',
        install_requires=['injectool==1.1.*'],
        keywords='binding pyviews python mvvm tkviews wxviews',
        packages=find_packages(exclude=['*.tests']))


_HERE = dirname(__file__)


def _get_version() -> str:
    with open(join_path(_HERE, "pyviews", "__init__.py")) as package:
        pattern = re.compile(r"__version__ = '(.*)'")
        match = pattern.search(package.read())
        return match.group(1)


def _get_long_description() -> str:
    readme_path = join_path(_HERE, "README.md")
    with codecs.open(readme_path, encoding="utf-8") as readme:
        return "\n" + readme.read()


if __name__ == '__main__':
    setup_package()
