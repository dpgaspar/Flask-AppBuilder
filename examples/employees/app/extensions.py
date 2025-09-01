from flask_appbuilder import AppBuilder
from flask_appbuilder.utils.legacy import get_sqla_class

from .security import MySecurityManager

db = get_sqla_class()()
appbuilder = AppBuilder(security_manager_class=MySecurityManager)
