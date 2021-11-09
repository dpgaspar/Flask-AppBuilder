from flask_appbuilder.baseviews import BaseView, expose

from . import appbuilder


class MyView(BaseView):
    route_base = "/myview"

    @expose("/method1/<string:param1>")
    def method1(self, param1):
        # do something with param1
        # and return to previous page or index
        param1 = "Hello %s" % (param1)
        return param1

    @expose("/method2/<string:param1>")
    def method2(self, param1):
        # do something with param1
        # and render template with param
        param1 = "Goodbye %s" % (param1)
        return param1


appbuilder.add_view_no_menu(MyView())
