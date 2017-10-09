from os.path import abspath
from pyviews.tk.app import register_dependencies, launch
from pyviews.core import ioc

ioc.register_value('views_folder', abspath('views'))

def run_sandbox():
    register_dependencies()
    launch('app')

if __name__ == '__main__':
    run_sandbox()
