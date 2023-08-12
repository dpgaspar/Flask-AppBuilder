from flask_appbuilder import ModelView
from flask_appbuilder.fields import AJAXSelectField
from flask_appbuilder.fieldwidgets import Select2AJAXWidget, Select2SlaveAJAXWidget
from flask_appbuilder.models.sqla.interface import SQLAInterface
from wtforms import validators


from . import appbuilder, db
from .models import (
    Contact, ContactGroup, ContactGroup2, ContactSubGroup, ContactSubGroup2
)


class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)

    list_columns = ["name", "contact_group.name", "contact_sub_group.name"]

    base_order = ("name", "asc")
    show_fieldsets = [
        (
            "Summary",
            {"fields": ["name", "gender", "contact_group", "contact_sub_group"]},
        ),
        (
            "Personal Info",
            {
                "fields": [
                    "address",
                    "birthday",
                    "personal_phone",
                    "personal_celphone",
                ],
                "expanded": False,
            },
        ),
    ]

    add_fieldsets = [
        (
            "Summary",
            {
                "fields": [
                    "name",
                    "gender",
                    "contact_group2",
                    "contact_sub_group2",
                    "contact_group",
                    "contact_sub_group",
                ]
            },
        ),
        (
            "Personal Info",
            {
                "fields": [
                    "address",
                    "birthday",
                    "personal_phone",
                    "personal_celphone",
                ],
                "expanded": False,
            },
        ),
    ]

    edit_fieldsets = [
        (
            "Summary",
            {
                "fields": [
                    "name",
                    "gender",
                    "contact_group2",
                    "contact_sub_group2",
                    "contact_group",
                    "contact_sub_group",
                ]
            },
        ),
        (
            "Personal Info",
            {
                "fields": [
                    "address",
                    "birthday",
                    "personal_phone",
                    "personal_celphone",
                ],
                "expanded": False,
            },
        ),
    ]

    add_form_extra_fields = {
        "contact_group": AJAXSelectField(
            "Contact Group",
            description="Group field populated with AJAX",
            datamodel=datamodel,
            validators=[validators.DataRequired()],
            col_name="contact_group",
            widget=Select2AJAXWidget(
                endpoint="/contactmodelview/api/column/add/contact_group"
            ),
        ),
        "contact_sub_group": AJAXSelectField(
            "Sub Contact Group",
            description="Sub Group related to Group",
            datamodel=datamodel,
            validators=[validators.DataRequired()],
            col_name="contact_sub_group",
            widget=Select2SlaveAJAXWidget(
                master_id="contact_group",
                endpoint="/contactmodelview/api/column/add/contact_sub_group?_flt_0_contact_group={{ID}}",
            ),
        ),
        "contact_group2": AJAXSelectField(
            "Contact Group 2",
            description="Group field populated with AJAX",
            datamodel=datamodel,
            col_name="contact_group2",
            widget=Select2AJAXWidget(
                endpoint="/contactmodelview/api/column/add/contact_group2"
            ),
        ),
        "contact_sub_group2": AJAXSelectField(
            "Sub Contact Group 2",
            description="Sub Group related to Group",
            datamodel=datamodel,
            col_name="contact_sub_group2",
            widget=Select2SlaveAJAXWidget(
                master_id="contact_group2",
                endpoint="/contactmodelview/api/column/add/contact_sub_group2?_flt_0_contact_group2={{ID}}",
            ),
        ),
    }

    edit_form_extra_fields = add_form_extra_fields


class GroupModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactModelView]


class Group2ModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup2)
    related_views = [ContactModelView]


class SubGroupModelView(ModelView):
    datamodel = SQLAInterface(ContactSubGroup)
    list_columns = ["name", "contact_group.name"]
    add_columns = ["name", "contact_group"]
    edit_columns = ["name", "contact_group"]
    show_columns = ["name", "contact_group"]
    related_views = [ContactModelView]


class SubGroup2ModelView(ModelView):
    datamodel = SQLAInterface(ContactSubGroup2)
    list_columns = ["name", "contact_group2.name"]
    add_columns = ["name", "contact_group2"]
    edit_columns = ["name", "contact_group2"]
    show_columns = ["name", "contact_group2"]
    related_views = [ContactModelView]


db.create_all()
appbuilder.add_view(
    GroupModelView,
    "List Groups",
    icon="fa-folder-open-o",
    category="Contacts",
    category_icon="fa-envelope",
)
appbuilder.add_view(
    Group2ModelView,
    "List Groups2",
    icon="fa-folder-open-o",
    category="Contacts",
    category_icon="fa-envelope",
)
appbuilder.add_view(
    SubGroupModelView,
    "List Sub Groups",
    icon="fa-folder-open-o",
    category="Contacts",
    category_icon="fa-envelope",
)
appbuilder.add_view(
    SubGroup2ModelView,
    "List Sub Groups2",
    icon="fa-folder-open-o",
    category="Contacts",
    category_icon="fa-envelope",
)
appbuilder.add_view(
    ContactModelView, "List Contacts", icon="fa-envelope", category="Contacts"
)
