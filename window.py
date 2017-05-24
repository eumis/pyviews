from parsing.parser import loadApp, loadPage

def init(appPath):
    global tk
    tk = loadApp(appPath)
    tk.state('zoomed')

def show_page(pagePath):
    for widget in tk.winfo_children():
        widget.destroy()
    controls = loadPage(pagePath, tk)

def show():
    tk.mainloop()