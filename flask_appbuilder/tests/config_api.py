import os

from sqlalchemy.engine import Engine
from sqlalchemy import event

SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
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


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
