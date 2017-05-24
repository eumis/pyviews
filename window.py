from parsing.parser import loadApp, loadPage

def init(appPath):
    global tk
    tk = loadApp(appPath)
    tk.state('zoomed')

def showPage(pagePath):
    controls = loadPage(pagePath, tk)

def show():
    tk.mainloop()