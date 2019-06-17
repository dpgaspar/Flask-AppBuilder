import os

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.db")
app.config["CSRF_ENABLED"] = True
app.config["SECRET_KEY"] = "thisismyscretkey"

db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

app.run(host="0.0.0.0", port=8080, debug=True)
