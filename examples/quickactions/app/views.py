from flask import redirect
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.actions import action

from app import appbuilder
from .models import ContactGroup


class GroupModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    list_columns = ['name']

    @action("myaction", "Do something on this record", "Do you really want to?", "fa-rocket")
    def myaction(self, item):
        """
            do something with the item record
        """
        return redirect(self.get_redirect())

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(GroupModelView, "List Groups", icon="fa-folder-open-o",
                    category="Contacts", category_icon='fa-envelope')
