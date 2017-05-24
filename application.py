import os
from parsing.parser import load_view

def init(view):
    global app
    app = load_view(get_view_path(view))

def show_view(view):
    for widget in app.winfo_children():
        widget.destroy()
    load_view(get_view_path(view), app)

def get_view_path(view):
    return os.path.abspath('sandbox/' + view + '.xml')

def run():
    app.mainloop()
