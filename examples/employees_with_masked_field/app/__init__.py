import logging

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from sqlalchemy import event
from sqlalchemy.engine import Engine

from .mysecurity import MySecurityManager # TESTING

#ADDED THE BELOW SETTINGS for logging:
logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object("config")
db = SQLA(app)
appbuilder = AppBuilder(app, db.session, 
			security_manager_class=MySecurityManager, # TESTING
			base_template="my_baselayout.html"   # THIS IS MANDATORY - will load some modified Javascripts
			)  

# THIS IS MANDATORY
# ADDED THIS global variable, visible everywhere, with "locale definitions" for important languages:
from .locale import LocaleDefinitions
gbl_locale_definitions = LocaleDefinitions(appbuilder)
app.jinja_env.globals['gbl_locale_definitions'] = gbl_locale_definitions #<<- MUST use this, for jinja visibility



@event.listens_for(Engine, "connect")               #<<<-- COMMENT THIS BLOCK IF NOT USING SQLITE, i.e. MYSQL)
def set_sqlite_pragma(dbapi_connection, connection_record):     
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


from . import models, views  # noqa

