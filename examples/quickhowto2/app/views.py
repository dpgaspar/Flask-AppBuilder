import calendar

from flask import flash, Markup, redirect, url_for
from flask_appbuilder import (
    action, aggregate_count, BaseView, expose, GroupByChartView, has_access, ModelView
)
from flask_appbuilder._compat import as_unicode
from flask_appbuilder.models.sqla.filters import FilterStartsWith
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.views import MultipleView, SimpleFormView
from flask_appbuilder.widgets import (
    FormVerticalWidget, ListBlock, ListWidget, ShowBlockWidget
)

from . import appbuilder, db
from .forms import TestForm
from .models import (
    Contact, ContactGroup, FloatModel, Gender, Product, ProductManufacturer, ProductModel
)


def fill_gender():
    try:
        db.session.add(Gender(name="Male"))
        db.session.add(Gender(name="Female"))
        db.session.commit()
    except Exception:
        db.session.rollback()


class TestForm(SimpleFormView):
    form = TestForm
    form_title = "This is my Test Form"
    default_view = "this_form_get"
    message = "My form submitted"

    def form_post(self, form):
        # process form
        flash(as_unicode(self.message), "info")


class ProductModelView(ModelView):
    datamodel = SQLAInterface(ProductModel)


class ProductView(ModelView):
    datamodel = SQLAInterface(Product)
    list_columns = ["name", "product_manufacturer", "product_model"]
    add_columns = ["name", "product_manufacturer", "product_model"]
    edit_columns = ["name", "product_manufacturer", "product_model"]
    add_widget = FormVerticalWidget
    base_filters = [["name", FilterStartsWith, "P"]]


class ProductManufacturerView(ModelView):
    datamodel = SQLAInterface(ProductManufacturer)
    related_views = [ProductModelView, ProductView]


class MyListWidget(ListWidget):
    template = "widgets/list.html"


class MyListWidgetOverride(ListWidget):
    template = "widgets/list_override.html"


class ContactModelView2(ModelView):
    datamodel = SQLAInterface(Contact)
    list_columns = ["name", "personal_celphone", "birthday", "contact_group.name"]
    add_form_query_rel_fields = {"gender": [["name", FilterStartsWith, "F"]]}
    search_form_query_rel_fields = {"gender": [["name", FilterStartsWith, "F"]]}
    list_template = "mylist.html"
    list_widget = MyListWidgetOverride
    extra_args = {"widget_arg": "WIDGET"}

    @expose("/jsonexp")
    def jsonexp(self):
        active_filters = self._filters.get_filters_values_tojson()
        return self.render_template(
            "list_angulajs.html",
            api_url=url_for(self.__class__.__name__ + ".api"),
            label_columns=self._label_columns_json(),
            active_filters=active_filters,
        )


class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)

    add_widget = FormVerticalWidget
    show_widget = ShowBlockWidget

    list_columns = ["name", "personal_celphone", "birthday", "contact_group.name"]

    list_template = "list_contacts.html"
    list_widget = ListBlock
    show_template = "show_contacts.html"

    extra_args = {"extra_arg_obj1": "Extra argument 1 injected"}
    base_order = ("name", "asc")

    show_fieldsets = [
        ("Summary", {"fields": ["name", "gender", "contact_group"]}),
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
        ("Summary", {"fields": ["name", "gender", "contact_group"]}),
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
        ("Summary", {"fields": ["name", "gender", "contact_group"]}),
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

    @action(
        "muldelete",
        "Delete",
        Markup("<p>Delete all Really?</p><p>Ok then...</p>"),
        "fa-rocket",
    )
    def muldelete(self, items):
        self.datamodel.delete_all(items)
        self.update_redirect()
        return redirect(self.get_redirect())


class GroupModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactModelView]
    show_template = "appbuilder/general/model/show_cascade.html"
    list_columns = ["name", "extra_col", "extra_col2"]


class FloatModelView(ModelView):
    datamodel = SQLAInterface(FloatModel)


class ContactChartView(GroupByChartView):
    datamodel = SQLAInterface(Contact)
    chart_title = "Grouped contacts"
    label_columns = ContactModelView.label_columns
    chart_type = "PieChart"

    definitions = [
        {"group": "contact_group.name", "series": [(aggregate_count, "contact_group")]},
        {"group": "gender", "series": [(aggregate_count, "gender")]},
    ]


def pretty_month_year(value):
    return calendar.month_name[value.month] + " " + str(value.year)


def pretty_year(value):
    return str(value.year)


class ContactTimeChartView(GroupByChartView):
    datamodel = SQLAInterface(Contact)

    chart_title = "Grouped Birth contacts"
    chart_type = "AreaChart"
    label_columns = ContactModelView.label_columns
    definitions = [
        {
            "group": "month_year",
            "formatter": pretty_month_year,
            "series": [(aggregate_count, "contact_group")],
        },
        {
            "group": "year",
            "formatter": pretty_year,
            "series": [(aggregate_count, "contact_group")],
        },
    ]


class MultipleViewsExp(MultipleView):
    views = [ContactChartView, ContactTimeChartView]


class PostTweet(BaseView):
    default_view = "tweet"

    @expose("/tweet/")
    @has_access
    def tweet(self):
        resp = self.appbuilder.sm.oauth_remotes["twitter"].post(
            "statuses/update.json", data={"status": "The text we want to tweet"}
        )
        if resp.status == 403:
            flash("Your tweet was too long. {0}".format(resp.raw_data))
        else:
            flash("Successfully tweeted your tweet (ID: #%s)" % resp.data["id"])
        return redirect(self.appbuilder.get_url_for_index)


fill_gender()

appbuilder.add_view(
    GroupModelView,
    "List Groups",
    icon="fa-folder-open-o",
    category="Contacts",
    category_icon="fa-envelope",
)
appbuilder.add_view(
    ContactModelView, "List Contacts", icon="fa-envelope", category="Contacts"
)
appbuilder.add_view(
    ContactModelView2, "List Contacts 2", icon="fa-envelope", category="Contacts"
)
appbuilder.add_view(
    FloatModelView, "List Float Model", icon="fa-envelope", category="Contacts"
)
appbuilder.add_view(
    MultipleViewsExp, "Multiple Views", icon="fa-envelope", category="Contacts"
)
appbuilder.add_separator("Contacts")
appbuilder.add_view(
    ContactChartView, "Contacts Chart", icon="fa-dashboard", category="Contacts"
)
appbuilder.add_view(
    ContactTimeChartView,
    "Contacts Birth Chart",
    icon="fa-dashboard",
    category="Contacts",
)

appbuilder.add_view(
    ProductManufacturerView,
    "List Manufacturer",
    icon="fa-folder-open-o",
    category="Products",
    category_icon="fa-envelope",
)
appbuilder.add_view(
    ProductModelView, "List Models", icon="fa-envelope", category="Products"
)
appbuilder.add_view(
    ProductView, "List Products", icon="fa-envelope", category="Products"
)
appbuilder.add_link(
    "ContacModelView_lnk",
    "ContactModelView.add",
    icon="fa-envelope",
    label="Add Contact",
)
appbuilder.add_view(TestForm, "My form View", icon="fa-group", label="My Test form")
appbuilder.add_view(PostTweet, "Tweet", icon="fa-twitter", label="Tweet")

appbuilder.add_link("Index", "MyIndexView.index")
appbuilder.security_cleanup()
