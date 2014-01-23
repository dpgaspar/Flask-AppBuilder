from flask import redirect, request, session
from flask.ext.babelpkg import refresh
from ..baseviews import BaseView, expose


class LocaleView(BaseView):
    route_base = '/lang'

    @expose('/<string:locale>')
    def index(self, locale):
        session['locale'] = locale
        refresh()
        return redirect(self._get_redirect())


