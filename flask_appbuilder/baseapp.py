import logging

from .views import IndexView
from filters import TemplateFilters
from flask import Blueprint
from flask.ext.babelpkg import gettext as _gettext, lazy_gettext
from flask.ext.appbuilder.babel.manager import BabelManager
from flask.ext.appbuilder import translations
from .security.manager import SecurityManager
from menu import Menu

log = logging.getLogger(__name__)

class BaseApp(object):
    """
        This is the base class for the all framework.
        Will hold your flask app object, all your views, and security classes.
        
        initialize your application like this::
            
            app = Flask(__name__)
            app.config.from_object('config')
            db = SQLAlchemy(app)
            baseapp = BaseApp(app, db)
        
    """
    baseviews = []
    app = None
    db = None
    
    sm = None
    """ Security Manager """
    bm = None
    """ Babel Manager """
    app_name = ""
    app_theme = ''
    app_icon = None
    
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
            
            :param app:
                The flask app object
            :param db:
                The SQLAlchemy db object
            :param menu:
                optional, a previous contructed menu
            :param indexview:
                optional, your customized indexview
            :param static_folder:
                optional, your override for the global static folder
            :param static_url_path:
                optional, your override for the global static url path
        """
        self.app = app
        self.db = db
                    
        self.sm = SecurityManager(app, db.session)
        self.bm = BabelManager(app, pkg_translations=translations)
        
        if menu:
            self.menu = menu
            self._add_menu_permissions()
        else:
            self.menu = Menu()
        
        self.app.before_request(self.sm.before_request)
        
        self._init_config_parameters()
        self.indexview = indexview or IndexView
        self.static_folder = static_folder
        self.static_url_path = static_url_path
        self._add_admin_views()
        self._add_global_static()
        self._add_global_filters()        
    
        # Creating Developer's models
        self.db.create_all()
        
    
    def _init_config_parameters(self):
        if 'APP_NAME' in self.app.config:
            self.app_name = self.app.config['APP_NAME']
        else:
            self.app_name = 'F.A.B.'
        if 'APP_ICON' in self.app.config:
            self.app_icon = self.app.config['APP_ICON']
        if 'APP_THEME' in self.app.config:
            self.app_theme = self.app.config['APP_THEME']
        else:
            self.app_theme = ''
        if 'LANGUAGES' in self.app.config:
            self.languages = self.app.config['LANGUAGES']
        else:
            self.languages = {
                'en': {'flag':'gb', 'name':'English'},
                }
    
    def _add_global_filters(self):
        self.template_filters = TemplateFilters(self.app, self.sm)

    def _add_global_static(self):
        bp = Blueprint('baseapp', __name__, url_prefix='/static',
                template_folder='templates', static_folder = self.static_folder, static_url_path = self.static_url_path)
        self.app.register_blueprint(bp)

    def _add_admin_views(self):
        self.indexview = self.indexview()
        self.add_view_no_menu(self.indexview)
        self.bm.register_views(self)
        self.sm.register_views(self)

    def _init_view_session(self, baseview_class):
        if baseview_class.datamodel.session == None:
            baseview_class.datamodel.session = self.db.session
        return baseview_class()
    
    def _add_permissions_menu(self, name):
        try:
            self.sm.add_permissions_menu(name)
        except:
            log.error("Add Permission on Menu Error")
    
    
    def _add_menu_permissions(self):
        for category in self.menu.get_list():
            self._add_permissions_menu(category.name)
            for item in category.childs:
                self._add_permissions_menu(item.name)
    
    def add_view(self, baseview, name, href = "", icon = "", category = ""):
        """
            Add your views associated with menus using this method.
            
            :param baseview:
                A BaseView type class instantiated.
            :param name:
                The string name that will be displayed on the menu.
            :param href:
                Override the generated href for the menu. if non provided default_view from view will be set as href.
            :param icon:
                Font-Awesome icon name, optional.
            :param category:
                The menu category where the menu will be included, if non provided the view will be acessible as a top menu.
                
            Examples::
            
                baseapp = BaseApp(app, db)
                # Register a view, rendering a top menu without icon
                baseapp.add_view(MyGeneralView, "My View")
                # Register a view, a submenu "Other View" from "Other" with a phone icon
                baseapp.add_view(MyOtherGeneralView, "Other View", icon='fa-phone', category="Others")
                # Add a link
                baseapp.add_link("google", href="www.google.com", icon = "fa-google-plus")
        """
        log.info("Registering class %s on menu %s.%s" % (baseview.__class__.__name__, category,name))
        if baseview not in self.baseviews:
            baseview.baseapp = self
            self.baseviews.append(baseview)
            self._process_ref_related_views()
            self.register_blueprint(baseview)
            self._add_permission(baseview)
        self.add_link(name = name, href = href, icon = icon, category = category, baseview = baseview)
        
    def add_link(self, name, href, icon = "", category = "", baseview = None):
        """
            Add your own links to menu using this method
            
            :param name:
                The string name that will be displayed on the menu.
            :param href:
                Override the generated href for the menu.
            :param icon:
                Bootstrap included icon name
            :param category:
                The menu category where the menu will be included        
        """
        self.menu.add_link(name = name, href = href, icon = icon, 
                        category = category, baseview = baseview)
        self._add_permissions_menu(name)
        if category:
            self._add_permissions_menu(category)

    def add_separator(self, category):
        """
            Add a separator to the menu, you will sequentially create the menu
            
            :param category:
                The menu category where the separator will be included.                    
        """
        self.menu.add_separator(category)

    def add_view_no_menu(self, baseview, endpoint = None, static_folder = None):
        """
            Add your views without creating a menu.
            
            :param baseview:
                A BaseView type class instantiated.
                    
        """
        if baseview not in self.baseviews:
            baseview.baseapp = self
            self.baseviews.append(baseview)
            self._process_ref_related_views()
            self.register_blueprint(baseview, endpoint = endpoint, static_folder = static_folder)
            self._add_permission(baseview)

    def _add_permission(self, baseview):
        try:
            self.sm.add_permissions_view(baseview.base_permissions, baseview.__class__.__name__)
        except:
            log.error("Add Permission on View Error")
        
    def register_blueprint(self, baseview, endpoint = None, static_folder = None):
        self.app.register_blueprint(baseview.create_blueprint(self,  endpoint = endpoint, static_folder = static_folder))

    def _process_ref_related_views(self):
        try:
            for view in self.baseviews:
                if hasattr(view, 'related_views'):
                    for rel_class in view.related_views:
                        for v in self.baseviews:
                            if isinstance(v, rel_class) and v not in view._related_views:
                                view._related_views.append(v)
        except:
            raise Exception('Use related_views with classes, not instances')
        
