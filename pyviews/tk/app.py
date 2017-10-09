from os.path import abspath
from pyviews.core import ioc
from pyviews.tk.parsing import convert_to_node

ioc.register_value('convert_to_node', convert_to_node)
ioc.register_value('views_folder', abspath('views'))
