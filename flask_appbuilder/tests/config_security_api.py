import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = (
    os.environ.get("SQLALCHEMY_DATABASE_URI")
    or "postgresql+psycopg2://pguser:pguserpassword@127.0.0.1:5432/app"
)

FAB_ADD_SECURITY_API = True
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
