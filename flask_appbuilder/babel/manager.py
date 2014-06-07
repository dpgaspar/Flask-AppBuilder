from flask import session
from flask.ext.babelpkg import Babel
from ..basemanager import BaseManager
from .. import translations
from .views import LocaleView


class BabelManager(BaseManager):

    babel = None
    locale_view = None

    def __init__(self, appbuilder):
        super(BabelManager, self).__init__(appbuilder)
        app = appbuilder.get_app
        app.config.setdefault('BABEL_DEFAULT_LOCALE', 'en')
        self.babel = Babel(app, translations)
        self.babel.locale_selector_func = self.get_locale

    def register_views(self):
        self.locale_view = LocaleView()
        self.appbuilder.add_view_no_menu(self.locale_view)

    @property
    def babel_default_locale(self):
        return self.appbuilder.get_app.config['BABEL_DEFAULT_LOCALE']

    def get_locale(self):
        locale = session.get('locale')
        if locale:
            return locale
        session['locale'] = self.babel_default_locale
        return session['locale']
