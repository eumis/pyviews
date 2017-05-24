import os
from window import init, show as show_window
from sandbox.commands import show_page

init(os.path.abspath('sandbox/app.xml'))
show_page('changepage')


show_window()
