from flask.ext.appbuilder.menu import Menu
from flask.ext.appbuilder.baseapp import BaseApp
from flask.ext.appbuilder.views import GeneralView
from flask.ext.appbuilder.filters import *



menu = Menu()

baseapp = BaseApp(app, menu)

