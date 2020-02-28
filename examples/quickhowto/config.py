import os

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = "thisismyscretkey"
SQLALCHEMY_TRACK_MODIFICATIONS = False
WTF_CSRF_ENABLED = False
FAB_API_SWAGGER_UI = True
FAB_ROLES = {
    "ReadOnly": [
        [".*", "can_get"],
        [".*", "can_info"],
        [".*", "can_list"],
        [".*", "can_show"],
    ]
}

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")

