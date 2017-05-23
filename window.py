from parsing.parser import loadApp

def init(appPath):
    tk = loadApp(appPath)
    tk.state('zoomed')
    tk.mainloop()
