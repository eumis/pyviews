from shutil import rmtree
from os.path import abspath
from setup import setup_package

def clean():
    try:
        directories = ['build', 'dist', 'pyviews.egg-info']
        for directory in directories:
            path = abspath(directory)
            rmtree(path)
    except FileNotFoundError:
        pass

if __name__ == '__main__':
    clean()
    setup_package()
