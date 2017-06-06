from tkinter import messagebox

def show_message(title, message):
    messagebox.showinfo(title, message)

def get_color(index):
    return 'yellow' if index % 2 != 0 else 'white'
