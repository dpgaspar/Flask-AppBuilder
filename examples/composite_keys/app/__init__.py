from flask import Flask

from .views import ItemModelView, RackModelView, InventoryModelView, DatacenterModelView
from .extensions import appbuilder


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")
    with app.app_context():
        appbuilder.init_app(app)
        appbuilder.add_view(
            DatacenterModelView,
            "List Datacenters",
            icon="fa-folder-open-o",
            category="Datacenters",
            category_icon="fa-envelope",
        )
        appbuilder.add_view(
            RackModelView, "List Racks", icon="fa-envelope", category="Datacenters"
        )
        appbuilder.add_view(
            ItemModelView,
            "List Items",
            icon="fa-folder-open-o",
            category="Datacenters",
            category_icon="fa-envelope",
        )
        appbuilder.add_view(
            InventoryModelView,
            "List Inventory",
            icon="fa-envelope",
            category="Datacenters",
        )

    return app
