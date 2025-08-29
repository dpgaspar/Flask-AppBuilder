import os

from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder.utils.legacy import get_sqla_class

# Get the SQLA class
SQLA = get_sqla_class()

# Create app factory
def create_app():
    app = Flask(__name__)
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.db")
    app.config["CSRF_ENABLED"] = True
    app.config["SECRET_KEY"] = "thisismyscretkey"
    
    db = SQLA()
    appbuilder = AppBuilder()
    
    with app.app_context():
        db.init_app(app)
        appbuilder.init_app(app, db.session)
    
    return app

# Create the app
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
