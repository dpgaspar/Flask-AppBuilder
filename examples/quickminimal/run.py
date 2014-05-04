import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.appbuilder.baseapp import BaseApp

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'thisismyscretkey'

app = Flask(__name__)
db = SQLAlchemy(app)
genapp = BaseApp(app, db)

app.run(host='0.0.0.0', port=8080, debug=True)
