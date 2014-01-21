from flask.ext.babelpkg import Babel
from flask import session
from views import LocaleView

class  BabelManager(object):

    babel = None
    basel_default_locale = ''

    def __init__(self, app, pkg_translations):
        self.babel = Babel(app, pkg_translations)
        self.basel_default_locale = self._get_default_locale(app)
        self.babel.locale_selector_func = self.get_locale

    def register_views(self, baseapp):    
        baseapp.add_view_no_menu(LocaleView())
    
    def _get_default_locale(self, app):
        if 'BABEL_DEFAULT_LOCALE' in app.config:
            self.basel_default_locale = app.config['BABEL_DEFAULT_LOCALE']
        else:
            self.basel_default_locale = 'en'

    def get_locale(self):
        locale = session.get('locale')
        if locale:
            return locale
        session['locale'] = self.basel_default_locale
        return session['locale']


    
