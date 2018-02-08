from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface


from app import db, appbuilder
from .models import Datacenter, Rack, Item, Inventory


class InventoryModelView(ModelView):
    datamodel = SQLAInterface(Inventory)
    list_columns = ["item", "rack"]
    add_columns = ["item", "rack"]
    edit_columns = ["item", "rack"]
    show_columns = ["item", "rack"]


class RackModelView(ModelView):
    datamodel = SQLAInterface(Rack)
    list_columns = ["num", "datacenter.name"]
    add_columns = ["num", "datacenter"]
    edit_columns = ["num", "datacenter"]
    show_columns = ["num", "datacenter"]


class ItemModelView(ModelView):
    datamodel = SQLAInterface(Item)
    list_columns = ["serial_number", "model"]
    add_columns = ["serial_number", "model"]
    edit_columns = ["serial_number", "model"]
    show_columns = ["serial_number", "model"]


class DatacenterModelView(ModelView):
    datamodel = SQLAInterface(Datacenter)
    list_columns = ["name", "address"]
    add_columns = ["name", "address"]
    edit_columns = ["name", "address"]
    show_columns = ["name", "address"]
    related_views = [RackModelView]
    show_template = 'appbuilder/general/model/show_cascade.html'
    edit_template = 'appbuilder/general/model/edit_cascade.html'



db.create_all()
appbuilder.add_view(DatacenterModelView, "List Datacenters", icon="fa-folder-open-o", category="Datacenters", category_icon='fa-envelope')
appbuilder.add_view(RackModelView, "List Racks", icon="fa-envelope", category="Datacenters")
appbuilder.add_view(ItemModelView, "List Items", icon="fa-folder-open-o", category="Datacenters", category_icon='fa-envelope')
appbuilder.add_view(InventoryModelView, "List Inventory", icon="fa-envelope", category="Datacenters")
