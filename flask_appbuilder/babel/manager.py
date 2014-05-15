from flask import session
from flask.ext.babelpkg import Babel
from ..basemanager import BaseManager
from .. import translations
from .views import LocaleView


class BabelManager(BaseManager):

    babel = None
    babel_default_locale = ''
    locale_view = None

    def __init__(self, appbuilder):
        super(BabelManager, self).__init__(appbuilder)
        self.babel = Babel(appbuilder.get_app, translations)
        self.babel_default_locale = self._get_default_locale(appbuilder.get_app)
        self.babel.locale_selector_func = self.get_locale

    def register_views(self):
        self.locale_view = LocaleView()
        self.appbuilder.add_view_no_menu(self.locale_view)

    @staticmethod
    def _get_default_locale(app):
        if 'BABEL_DEFAULT_LOCALE' in app.config:
            return app.config['BABEL_DEFAULT_LOCALE']
        else:
            return 'en'

    def get_locale(self):
        locale = session.get('locale')
        if locale:
            return locale
        session['locale'] = self.babel_default_locale
        return session['locale']
