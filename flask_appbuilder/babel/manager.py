
class  BabelManager(object)

    def __init__(self, babel):
        babel.localeselector = self.get_locale()
        
        
    def get_locale():
        locale = session.get('locale')
        if locale:
            return locale
        session['locale'] = BABEL_DEFAULT_LOCALE
        return session['locale']


    
