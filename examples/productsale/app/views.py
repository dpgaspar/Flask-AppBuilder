from models import Product, ProductType, Sale
from flask.ext.appbuilder.baseapp import BaseApp
from flask.ext.appbuilder.views import GeneralView, BaseView
from flask.ext.appbuilder.charts.views import ChartView
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.widgets import ListBlock

from app import app, db


class ProductPubView(GeneralView):
    datamodel = SQLAModel(Product, db.session)
    base_permissions = ['can_list', 'can_show']
    list_widget = ListBlock

    label_columns = {'photo_img': 'Photo'}

    list_columns = ['name', 'photo_img', 'price']
    search_columns = ['name', 'price', 'product_type']

class ProductView(GeneralView):
    datamodel = SQLAModel(Product, db.session)

class ProductTypeView(GeneralView):
    datamodel = SQLAModel(ProductType, db.session)
    related_views = [ProductView]


baseapp = BaseApp(app, db)

baseapp.add_view(ProductPubView(), "Our Products", icon="fa-folder-open-o")
baseapp.add_view(ProductView(), "List Products", icon="fa-folder-open-o", category="Management")
baseapp.add_separator("Management")
baseapp.add_view(ProductTypeView(), "List Product Types", icon="fa-envelope", category="Management")

