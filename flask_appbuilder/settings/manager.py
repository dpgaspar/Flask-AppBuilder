from flask_appbuilder import __version__
from models import Setting


class SettingsManager(object):
    def __init__(self, app, session):
        """
            SettingsManager contructor
            param app:
                The Flask app object
            param session:
                the database session for security tables, passed to BaseApp
        """
        self.app = app
        self.session = session
        version = self.get_installed_version()
        if not version:
            self.session.add(Setting(key='Version', value=__version__))
            self.session.commit()
        elif version != __version__:
            version.value = __version__
            self.session.merge(version)


    def get_installed_version(self):
        return self.session.query(Setting).filter(key='Version')

