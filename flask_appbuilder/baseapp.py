from flask import Blueprint
from flask.ext.babel import lazy_gettext
from flask.ext.babel import gettext as _gettext
from .security.views import (AuthView, ResetMyPasswordView, ResetPasswordView, 
                        UserDBGeneralView, UserOIDGeneralView, RoleGeneralView, PermissionViewGeneralView, 
                        ViewMenuGeneralView, PermissionGeneralView, PermissionView)
from .security.models import User, Role
from .security.access import SecurityManager
from .views import IndexView
from .babel.views import LocaleView
from menu import Menu
from filters import TemplateFilters

class BaseApp():

    lst_baseview = []
    app = None
    db = None
    sm = None
    
    app_name = ""
    menu = None
    indexview = None
    
    static_folder = None
    static_url_path = None
    
    template_filters = None
    
    languages = None
    admin = None
    _gettext = _gettext

    def __init__(self, app, db, lm, 
                    oid = None, 
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
            param lm:
                The LoginManager initialized flask-Login
            param oid:
                optional, The flask-openId
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
        self.init_db()
        self.sm = SecurityManager(db.session, 
                            self._get_auth_type(), 
                            self._get_role_admin(), 
                            self._get_role_public(), 
                            lm, 
                            oid = None)
        
        
        self._init_config_parameters()
        self.indexview = indexview or IndexView
        self.static_folder = static_folder
        self.static_url_path = static_url_path
        self._add_admin_views()
        self._add_global_static()
        self._add_global_filters()
    
    def init_db(self):
        from sqlalchemy.engine.reflection import Inspector

        inspector = Inspector.from_engine(self.db.engine)
        if 'ab_user' not in inspector.get_table_names():
            self.db.create_all()
            role_admin = Role()
            role_admin.name = self._get_role_admin()
            role_public = Role()
            role_public.name = self._get_role_public()
            user = User()
            user.first_name = 'Admin'
            user.last_name = ''
            user.username = 'admin'
            user.password = 'general'
            user.active = True
            user.role = role_admin

            self.db.session.add(role_admin)
            self.db.session.add(role_public)
            self.db.session.add(user)
            self.db.session.commit()
    
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
            return 1
      
    
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
        self.add_view_no_menu(AuthView())
        self.add_view_no_menu(ResetPasswordView())
        self.add_view_no_menu(ResetMyPasswordView())

        if self._get_auth_type() == 1:
            user_view = UserDBGeneralView()
        else:
            user_view = UserOIDGeneralView()
        self.add_view(user_view, "List Users"
                                        ,"/users/list","user",
                                        "Security")
        self.add_view(RoleGeneralView(), "List Roles","/roles/list","tags","Security")
        self.menu.add_separator("Security")
        self.add_view(PermissionViewGeneralView(), "Base Permissions","/permissions/list","lock","Security")
        self.add_view(ViewMenuGeneralView(), "Views/Menus","/viewmenus/list","list-alt","Security")
        self.add_view(PermissionGeneralView(), "Permission on Views/Menus","/permissionviews/list","lock","Security")

        
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
        #try:
        self.sm.add_permissions_menu(name)
        self.sm.add_permissions_menu(category)            
        #except:
        #    print "Add Permission on Menu Error: DB not created"
    

    def add_separator(self, category):
        self.menu.add_separator(category)

    def add_view_no_menu(self, baseview, endpoint = None, static_folder = None):
        if baseview not in self.lst_baseview:
            baseview.baseapp = self
            self.lst_baseview.append(baseview)
            self.register_blueprint(baseview, endpoint = endpoint, static_folder = static_folder)
            self._add_permission(baseview)

    def _add_permission(self, baseview):
        #try:
            self.sm.add_permissions_view(baseview.base_permissions, baseview.__class__.__name__)
        #except:
        #    print "Add Permission on View Error: DB not created?"
        
    def register_blueprint(self, baseview, endpoint = None, static_folder = None):
        self.app.register_blueprint(baseview.create_blueprint(self,  endpoint = endpoint, static_folder = static_folder))
