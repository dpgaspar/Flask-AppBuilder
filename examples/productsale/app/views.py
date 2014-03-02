from models import Product, ProductType, Sale
from flask.ext.appbuilder.baseapp import BaseApp
from flask.ext.appbuilder.views import GeneralView, BaseView
from flask.ext.appbuilder.charts.views import ChartView
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.widgets import ListThumbnail

from app import app, db


class ProductGeneralView(GeneralView):
    datamodel = SQLAModel(Product, db.session)

    #list_widget = ListThumbnail

    label_columns = {'photo_img': 'Photo'}

    list_columns = ['name', 'photo_img', 'price']
    search_columns = ['name']


class ProductTypeGeneralView(GeneralView):
    datamodel = SQLAModel(ProductType, db.session)
    related_views = [ProductGeneralView]




baseapp = BaseApp(app, db)
baseapp.add_view(ProductGeneralView(), "List Products", icon="fa-folder-open-o", category="Products")
baseapp.add_separator("Products")
baseapp.add_view(ProductTypeGeneralView(), "List Product Types", icon="fa-envelope", category="Products")

