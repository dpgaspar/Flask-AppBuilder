import logging
from flask_appbuilder.security.sqla.manager import SecurityManager
from .sec_models import MyUser
from .sec_views import MyUserDBModelView

log = logging.getLogger(__name__)


class MySecurityManager(SecurityManager):
    user_model = MyUser
    userdbmodelview = MyUserDBModelView

    def _has_view_access(self, user, permission_name, view_name):
        roles = user.roles
        for role in roles:
            lst = role.permissions
            if lst:
                for i in lst:
                    if (view_name == i.view_menu.name) and (permission_name == i.permission.name):
                        return True
                return False
            else:
                return False


    def add_user(self, username, first_name, last_name, email, role, password=''):
        """
            Generic function to create user
        """
        try:
            user = self.user_model()
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            user.active = True
            user.role_id = 1
            user.roles.append(role)
            user.password = password
            self.get_session.add(user)
            self.get_session.commit()
            log.info("Added user %s to user list." % username)
            return user
        except Exception as e:
            log.error(
                "Error adding new user to database. {0}".format(
                    str(e)))
            return False
