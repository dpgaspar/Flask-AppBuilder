from flask import Blueprint
from flask.ext.babel import lazy_gettext
from flask.ext.babel import gettext as _gettext
from .security.views import (AuthView, ResetMyPasswordView, ResetPasswordView, 
                        UserGeneralView, RoleGeneralView, PermissionViewGeneralView, 
                        ViewMenuGeneralView, PermissionGeneralView, PermissionView)
from .security.access import SecurityManager
from .views import IndexView
from .babel.views import LocaleView
from menu import Menu
from filters import TemplateFilters

class BaseApp():

    lst_baseview = []
    app = None
    db = None
    security_manager = None
    
    app_name = ""
    menu = None
    indexview = None
    
    static_folder = None
    static_url_path = None
    
    template_filters = None
    
    languages = None
    admin = None
    _gettext = _gettext

    def __init__(self, app, db, menu = None, indexview = None, static_folder='static/appbuilder', static_url_path='/appbuilder'):
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
        self.security_manager = SecurityManager(db.session, app.config['AUTH_ROLE_ADMIN'])
        
        self.app_name = app.config['APP_NAME']
        self.app_theme = app.config['APP_THEME']
        self.languages = app.config['LANGUAGES']
        self.indexview = indexview or IndexView
        self.static_folder = static_folder
        self.static_url_path = static_url_path
        self._add_admin_views()
        self.add_global_static()
        self.add_global_filters()
    
    def add_global_filters(self):
        self.template_filters = TemplateFilters(self.app, self.security_manager)

    def add_global_static(self):
        bp = Blueprint('baseapp', __name__, url_prefix='/static',
                template_folder='templates', static_folder = self.static_folder, static_url_path = self.static_url_path)
        self.app.register_blueprint(bp)

    def _add_admin_views(self):
        self.add_view_no_menu(self.indexview())
        self.add_view_no_menu(LocaleView())
        self.add_view_no_menu(AuthView())
        self.add_view_no_menu(ResetPasswordView())
        self.add_view_no_menu(ResetMyPasswordView())

        self.add_view(UserGeneralView(), "List Users"
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
        self.security_manager.add_permissions_menu(name)
        self.security_manager.add_permissions_menu(category)            
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
            self.security_manager.add_permissions_view(baseview.base_permissions, baseview.__class__.__name__)
        #except:
        #    print "Add Permission on View Error: DB not created?"
        
    def register_blueprint(self, baseview, endpoint = None, static_folder = None):
        self.app.register_blueprint(baseview.create_blueprint(self,  endpoint = endpoint, static_folder = static_folder))
