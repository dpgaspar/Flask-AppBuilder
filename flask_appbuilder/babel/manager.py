from flask.ext.babelpkg import Babel
from flask import session
from views import LocaleView


class BabelManager(object):

    babel = None
    babel_default_locale = ''

    def __init__(self, app, pkg_translations):
        self.babel = Babel(app, pkg_translations)
        self.babel_default_locale = self._get_default_locale(app)
        self.babel.locale_selector_func = self.get_locale

    @staticmethod
    def register_views(baseapp):
        baseapp.add_view_no_menu(LocaleView())

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
