'''Increments pyviews minor version'''

from os.path import join
from pyviews import __minor__ as minor_version

def increment_minor():
    '''Increments pyviews minor version'''
    init_path = join('pyviews', '__init__.py')
    with open(init_path) as init_file:
        source = init_file.read()
        min_version_format = '__minor__ = {0}'
        source = source.replace(min_version_format.format(minor_version),
                                min_version_format.format(minor_version + 1))
    with open(init_path, 'w') as init_file:
        init_file.write(source)

if __name__ == '__main__':
    increment_minor()
