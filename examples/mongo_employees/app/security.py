__author__ = 'dpgaspar'

from flask import redirect
from fab.flask_appbuilder.security.views import UserDBModelView
from fab.flask_appbuilder.security.mongoengine.manager import SecurityManager
from fab.flask_appbuilder.actions import action


class MyUserDBView(UserDBModelView):
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket", single=False)
    def muldelete(self, items):
        self.datamodel.delete_all(items)
        self.update_redirect()
        return redirect(self.get_redirect())


class MySecurityManager(SecurityManager):
    userdbmodelview = MyUserDBView
