from flask.ext.appbuilder.menu import Menu
from flask.ext.appbuilder.baseapp import BaseApp
from flask.ext.appbuilder.views import GeneralView

from app import app

def debug_rules():
    for rule in app.url_map.iter_rules():

        options = {}
        
        methods = ','.join(rule.methods)
	print "--------------------------------------------"
        print "EP: %s METH: %s" % (rule.endpoint, methods)
        print rule, rule.arguments
	print "--------------------------------------------"


menu = Menu()

menu.add_link(name="Google", href="http://www.google.com",icon="",parent_category="External Links")
baseapp = BaseApp(app, menu)

debug_rules()
