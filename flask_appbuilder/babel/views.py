from flask import redirect, request, session
from flask.ext.babel import refresh
from app import babel
from config import BABEL_DEFAULT_LOCALE
from ..views import BaseView, expose


class LocaleView(BaseView):
    route_base = '/lang'

    @expose('/<string:locale>')
    def index(self, locale):
        session['locale'] = locale
        refresh()
        return redirect(self._get_redirect())


@babel.localeselector
def get_locale():
    locale = session.get('locale')
    if locale:
        return locale
    session['locale'] = BABEL_DEFAULT_LOCALE
    return session['locale']
