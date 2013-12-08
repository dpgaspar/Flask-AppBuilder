from .babel.views import LocaleView
from .security.manager import SecurityManager
from .security.views import AuthDBView, AuthOIDView, ResetMyPasswordView, \
    ResetPasswordView, UserDBGeneralView, UserOIDGeneralView, RoleGeneralView, \
    PermissionViewGeneralView, ViewMenuGeneralView, PermissionGeneralView
    
from .views import IndexView
from filters import TemplateFilters
from flask import Blueprint
from flask.ext.babel import Babel, gettext as _gettext, lazy_gettext
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from menu import Menu
import os




AUTH_OID = 0
AUTH_DB = 1
AUTH_LDAP = 2


class BaseApp():
    """
        This is the base class for the all framework.
        Will hold your flask app object, all your views, and security classes.
        
        initialize your application like this::
            
            app = Flask(__name__)
            app.config.from_object('config')
            db = SQLAlchemy(app)
            baseapp = BaseApp(app, db)
        
    """
    lst_baseview = []
    app = None
    db = None
    # Security Manager
    sm = None
    
    app_name = ""
    app_theme = ''
    menu = None
    indexview = None
    
    static_folder = None
    static_url_path = None
    
    template_filters = None
    
    languages = None
    admin = None
    _gettext = _gettext

    def __init__(self, app, db, 
                    menu = None, 
                    indexview = None, 
                    static_folder='static/appbuilder', 
                    static_url_path='/appbuilder'):
        """
            BaseApp constructor
            param app:
                The flask app object
            param db:
                The SQLAlchemy db object
            param menu:
                optional, a previous contructed menu
            param indexview:
                optional, your customized indexview
            param static_folder:
                optional, your override for the global static folder
            param static_url_path:
                optional, your override for the global static url path
        """
        self.menu = menu or Menu()
        self.app = app
        self.db = db
        
        # Creating Developer's models
        self.db.create_all()
        
        lm = LoginManager()
        lm.init_app(app)
        lm.login_view = 'login'
        oid = OpenID(app)
        
        self.sm = SecurityManager(db.session, 
                            self._get_auth_type(), 
                            self._get_role_admin(), 
                            self._get_role_public(), 
                            lm, 
                            oid)
        
        
        self.app.before_request(self.sm.before_request)
        
        self._init_config_parameters()
        self.indexview = indexview or IndexView
        self.static_folder = static_folder
        self.static_url_path = static_url_path
        self._add_admin_views()
        self._add_global_static()
        self._add_global_filters()        
    
    
    def _init_config_parameters(self):
        if 'APP_NAME' in self.app.config:
            self.app_name = self.app.config['APP_NAME']
        else:
            self.app_name = 'AppBuilder'
        if 'APP_THEME' in self.app.config:
            self.app_theme = self.app.config['APP_THEME']
        else:
            self.app_theme = ''
        if 'LANGUAGES' in self.app.config:
            self.languages = self.app.config['LANGUAGES']
        else:
            self.languages = {
                'en': {'flag':'gb', 'name':'English'},
                'pt': {'flag':'pt', 'name':'Portugal'}
                }
    
    def _get_auth_type(self):
        if 'AUTH_TYPE' in self.app.config:
            return self.app.config['AUTH_TYPE']
        else:
            return AUTH_DB
      
    
    def _get_role_admin(self):
        if 'AUTH_ROLE_ADMIN' in self.app.config:
            return self.app.config['AUTH_ROLE_ADMIN']
        else:
            return 'Admin'
      
    def _get_role_public(self):
        if 'AUTH_ROLE_PUBLIC' in self.app.config:
            return self.app.config['AUTH_ROLE_PUBLIC']
        else:
            return 'Public'
      
    
    def _add_global_filters(self):
        self.template_filters = TemplateFilters(self.app, self.sm)

    def _add_global_static(self):
        bp = Blueprint('baseapp', __name__, url_prefix='/static',
                template_folder='templates', static_folder = self.static_folder, static_url_path = self.static_url_path)
        self.app.register_blueprint(bp)

    def _add_admin_views(self):
        self.add_view_no_menu(self.indexview())
        self.add_view_no_menu(LocaleView())
            
        self.add_view_no_menu(ResetPasswordView())
        self.add_view_no_menu(ResetMyPasswordView())

        if self._get_auth_type() == AUTH_DB:
            user_view = self._init_view_session(UserDBGeneralView)
            auth_view = AuthDBView()
        else:
            user_view = self._init_view_session(UserOIDGeneralView)
            auth_view = AuthOIDView()
            self.sm.oid.after_login_func = auth_view.after_login
        
        self.add_view_no_menu(auth_view)
        
        self.add_view(user_view, "List Users"
                                        ,"/users/list","user",
                                        "Security")
                                        
        self.add_view(self._init_view_session(RoleGeneralView), "List Roles","/roles/list","tags","Security")
        self.menu.add_separator("Security")
        self.add_view(self._init_view_session(PermissionViewGeneralView), "Base Permissions","/permissions/list","lock","Security")
        self.add_view(self._init_view_session(ViewMenuGeneralView), "Views/Menus","/viewmenus/list","list-alt","Security")
        self.add_view(self._init_view_session(PermissionGeneralView), "Permission on Views/Menus","/permissionviews/list","lock","Security")

    def _init_view_session(self, baseview_class):
        if baseview_class.datamodel.session == None:
            baseview_class.datamodel.session = self.db.session
        return baseview_class()
    
    
    
    def add_view(self, baseview, name, href = "", icon = "", category = ""):
        
        print "Registering:", category,".", name
        if baseview not in self.lst_baseview:
            baseview.baseapp = self
            self.lst_baseview.append(baseview)
            self.register_blueprint(baseview)
            self._add_permission(baseview)
        self.add_link(name = name, href = href, icon = icon, category = category, baseview = baseview)
        
    def add_link(self, name, href, icon = "", category = "", baseview = None):
        self.menu.add_link(name = name, href = href, icon = icon, 
                        category = category, baseview = baseview)
        try:
            self.sm.add_permissions_menu(name)
            self.sm.add_permissions_menu(category)            
        except:
            print "Add Permission on Menu Error: DB not created"
    

    def add_separator(self, category):
        self.menu.add_separator(category)

    def add_view_no_menu(self, baseview, endpoint = None, static_folder = None):
        if baseview not in self.lst_baseview:
            baseview.baseapp = self
            self.lst_baseview.append(baseview)
            self.register_blueprint(baseview, endpoint = endpoint, static_folder = static_folder)
            self._add_permission(baseview)

    def _add_permission(self, baseview):
        try:
            self.sm.add_permissions_view(baseview.base_permissions, baseview.__class__.__name__)
        except:
            print "Add Permission on View Error: DB not created?"
        
    def register_blueprint(self, baseview, endpoint = None, static_folder = None):
        self.app.register_blueprint(baseview.create_blueprint(self,  endpoint = endpoint, static_folder = static_folder))
