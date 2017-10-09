from os.path import abspath
from pyviews.tk.app import launch
from pyviews.core import ioc

ioc.register_value('views_folder', abspath('views'))

def run_sandbox():
    launch('app')

if __name__ == '__main__':
    run_sandbox()
