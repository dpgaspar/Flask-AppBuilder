__author__ = "dpgaspar"

from flask import redirect
from flask_appbuilder.actions import action
from flask_appbuilder.security.sqla.manager import SecurityManager
from flask_appbuilder.security.views import UserDBModelView


class MyUserDBView(UserDBModelView):
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket", single=False)
    def muldelete(self, items):
        self.datamodel.delete_all(items)
        self.update_redirect()
        return redirect(self.get_redirect())


class MySecurityManager(SecurityManager):
    userdbmodelview = MyUserDBView
