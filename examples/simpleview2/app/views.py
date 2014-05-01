from flask.ext.appbuilder.baseapp import BaseApp
from flask.ext.appbuilder.baseviews import BaseView
from flask.ext.appbuilder.baseviews import expose
from flask.ext.appbuilder.security.decorators import has_access
from app import app, db


class MyView(BaseView):

    default_view = 'method1'

    @expose('/method1/')
    @has_access
    def method1(self):
            # do something with param1
            # and return to previous page or index
        return 'Hello'

    @expose('/method2/<string:param1>')
    @has_access
    def method2(self, param1):
        # do something with param1
        # and render template with param
        param1 = 'Good by %s' % (param1)
        return param1


genapp = BaseApp(app, db)
genapp.add_view(MyView(), "Method1", category='My View')
genapp.add_view(MyView(), "Method2", href='/myview/method2/jonh', category='My View')


