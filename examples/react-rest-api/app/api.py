from flask_appbuilder import ModelRestApi, BaseView, has_access, expose
from flask_appbuilder.models.sqla.interface import SQLAInterface

from . import appbuilder, db
from .models import Contact, ContactGroup, Gender


def fill_gender():
    try:
        db.session.add(Gender(name="Male"))
        db.session.add(Gender(name="Female"))
        db.session.commit()
    except Exception:
        db.session.rollback()


db.create_all()
fill_gender()


class ContactModelApi(ModelRestApi):
    resource_name = "contact"
    datamodel = SQLAInterface(Contact)
    allow_browser_login = True
    list_columns = ["name", "address", 'birthday', 'contact_group.name']
    show_columns = [
            "name",
            "address",
            'birthday',
            'contact_group.name',
            "personal_celphone",
            "personal_phone",
            "gender.name"]


appbuilder.add_api(ContactModelApi)


class GroupModelApi(ModelRestApi):
   resource_name = "group"
   datamodel = SQLAInterface(ContactGroup)
   allow_browser_login = True


appbuilder.add_api(GroupModelApi)


class ReactRenderView(BaseView):
    @expose('/<string:param1>')
    @has_access
    def render_react(self, param1):
        self.update_redirect()
        return self.render_template('react.html',
                                    param1 = param1)


appbuilder.add_view_no_menu(ReactRenderView)
appbuilder.add_link("Contacts", href='/reactrenderview/contact', category='Contacts')
appbuilder.add_link("Groups", href='/reactrenderview/group', category='Contacts')

