from flask_appbuilder import AppBuilder

from . import MySecurityManager


appbuilder = AppBuilder(security_manager_class=MySecurityManager)
