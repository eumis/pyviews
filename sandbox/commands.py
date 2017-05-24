import os
from window import show_page as show
from tkinter import messagebox

def show_page(pageName):
    path = os.path.abspath('sandbox/' + pageName + '.xml')
    show(path)

def show_message(title, message):
    messagebox.showinfo(title, message)
