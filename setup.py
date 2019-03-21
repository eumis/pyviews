'''Pypi packaging setup'''

from setuptools import setup, find_packages
from pyviews import __version__ as pyviews_version

def setup_package():
    '''Package setup'''
    setup(
        name='pyviews',
        version=pyviews_version,
        description='Base package for xml views',
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
        keywords='binding tkviews tk tkinter pyviews python mvvm',
        packages=find_packages()

if __name__ == '__main__':
    setup_package()
