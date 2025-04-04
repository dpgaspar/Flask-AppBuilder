from importlib.metadata import PackageNotFoundError, version

try:
    fsqla_version = version("flask-sqlalchemy")
except PackageNotFoundError:
    raise ImportError("flask-sqlalchemy is not installed")

major_version = int(fsqla_version.split(".")[0])
if major_version < 3:
    from flask_appbuilder.models.sqla.base_legacy import SQLA
else:
    from flask_appbuilder.models.sqla.base import SQLA


db = SQLA()
