from models import Product, ProductType, Sale
from flask.ext.appbuilder.views import ModelView, BaseView
from flask.ext.appbuilder.charts.views import ChartView
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.widgets import ListBlock, ShowBlockWidget

from app import appbuilder, db


class ProductPubView(ModelView):
    datamodel = SQLAModel(Product)
    base_permissions = ['can_list', 'can_show']
    list_widget = ListBlock
    show_widget = ShowBlockWidget

    label_columns = {'photo_img': 'Photo'}

    list_columns = ['name', 'photo_img', 'price_label']
    search_columns = ['name', 'price', 'product_type']

    show_fieldsets = [
        ('Summary', {'fields': ['name', 'price_label', 'photo_img', 'product_type']}),
        (
            'Description',
            {'fields': ['description'], 'expanded': True}),
    ]

class ProductView(ModelView):
    datamodel = SQLAModel(Product)

class ProductTypeView(ModelView):
    datamodel = SQLAModel(ProductType)
    related_views = [ProductView]


db.create_all()
appbuilder.add_view(ProductPubView, "Our Products", icon="fa-folder-open-o")
appbuilder.add_view(ProductView, "List Products", icon="fa-folder-open-o", category="Management")
appbuilder.add_separator("Management")
appbuilder.add_view(ProductTypeView, "List Product Types", icon="fa-envelope", category="Management")

