from importlib.metadata import PackageNotFoundError, version
from typing import Type, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from flask_appbuilder.models.sqla.base import SQLA as SQLA
    from flask_appbuilder.models.sqla.base_legacy import SQLA as SQLALegacy
else:
    SQLA = None  # type: ignore
    SQLALegacy = None  # type: ignore


def is_flask_sqlalchemy_2() -> bool:
    """
    Check if the installed version of flask-sqlalchemy is 2.x.x.
    """
    try:
        fsqla_version = version("flask-sqlalchemy")
    except PackageNotFoundError:
        return False

    major_version = int(fsqla_version.split(".")[0])
    return major_version == 2


def get_sqla_class() -> Union[Type[SQLA], Type[SQLALegacy]]:
    """
    Returns the SQLA class based on the version of flask-sqlalchemy installed.
    """
    if is_flask_sqlalchemy_2():
        from flask_appbuilder.models.sqla.base_legacy import SQLA
    else:
        from flask_appbuilder.models.sqla.base import SQLA
    return SQLA
