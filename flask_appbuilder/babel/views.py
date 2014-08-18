from flask import redirect, request, session
from flask.ext.babelpkg import refresh
from ..baseviews import BaseView, expose


class LocaleView(BaseView):
    route_base = '/lang'

    default_view = 'index'

    @expose('/<string:locale>')
    def index(self, locale):
        session['locale'] = locale
        refresh()
        return redirect(self.get_redirect())


