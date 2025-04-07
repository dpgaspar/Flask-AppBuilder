from importlib.metadata import PackageNotFoundError, version
from typing import Type, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from flask_appbuilder.models.sqla.base import SQLA as SQLA
    from flask_appbuilder.models.sqla.base_legacy import SQLA as SQLALegacy
else:
    SQLA = None  # type: ignore
    SQLALegacy = None  # type: ignore


def get_sqla_class() -> Union[Type[SQLA], Type[SQLALegacy]]:
    """
    Returns the SQLA class based on the version of flask-sqlalchemy installed.
    """
    try:
        fsqla_version = version("flask-sqlalchemy")
    except PackageNotFoundError:
        raise ImportError("flask-sqlalchemy is not installed")

    major_version = int(fsqla_version.split(".")[0])
    if major_version < 3:
        from flask_appbuilder.models.sqla.base_legacy import SQLA
    else:
        from flask_appbuilder.models.sqla.base import SQLA
    return SQLA
