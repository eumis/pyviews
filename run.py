import application.api as api
from application.bootstrap import App

api.APP = App('sandbox')
api.show_view('changepage')
api.run_app()
