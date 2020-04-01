from flask_appbuilder.baseviews import BaseView
from flask_appbuilder import expose, has_access
from .Dashboard import Dash_App1, Dash_App2

from . import appbuilder


class MyDashAppCallBack(BaseView):
    route_base = "/"

    @has_access
    @expose("/dashboard_callback/")
    def methoddash(self):
        print("dash")
        return self.render_template("dash.html", dash_url=Dash_App1.url_base, appbuilder=appbuilder)


appbuilder.add_view_no_menu(MyDashAppCallBack())
appbuilder.add_link(
    "Dashboard Callback", href="/dashboard_callback/", icon="fa-list", category="Dash Demo", category_icon="fa-list"
)


class MyDashAppGraph(BaseView):
    route_base = "/"

    @has_access
    @expose("/dashboard_graph/")
    def methoddash(self):
        return self.render_template("dash.html", dash_url=Dash_App2.url_base, appbuilder=appbuilder)


appbuilder.add_view_no_menu(MyDashAppGraph())
appbuilder.add_link(
    "Dashboard Graph", href="/dashboard_graph/", icon="fa-list", category="Dash Demo", category_icon="fa-list"
)
