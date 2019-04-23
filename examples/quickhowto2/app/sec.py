import logging

from flask_appbuilder.security.sqla.manager import SecurityManager

from .sec_models import MyUser
from .sec_views import MyUserDBModelView


log = logging.getLogger(__name__)


class MySecurityManager(SecurityManager):
    user_model = MyUser
    userdbmodelview = MyUserDBModelView
