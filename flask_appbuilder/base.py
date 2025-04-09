from __future__ import annotations

from functools import reduce
import logging
from typing import Any, Callable, cast, Dict, List, Optional, Type, TYPE_CHECKING, Union

from flask import Blueprint, current_app, Flask, url_for
from flask_appbuilder import __version__
from flask_appbuilder.api.manager import OpenApiManager
from flask_appbuilder.babel.manager import BabelManager
from flask_appbuilder.const import (
    LOGMSG_ERR_FAB_ADD_PERMISSION_MENU,
    LOGMSG_ERR_FAB_ADD_PERMISSION_VIEW,
    LOGMSG_ERR_FAB_ADDON_IMPORT,
    LOGMSG_ERR_FAB_ADDON_PROCESS,
    LOGMSG_INF_FAB_ADD_VIEW,
    LOGMSG_INF_FAB_ADDON_ADDED,
    LOGMSG_WAR_FAB_VIEW_EXISTS,
)
from flask_appbuilder.extensions import db
from flask_appbuilder.filters import TemplateFilters
from flask_appbuilder.menu import Menu, MenuApiManager
from flask_appbuilder.views import IndexView, UtilView
from sqlalchemy.orm.session import Session as SessionBase

if TYPE_CHECKING:
    from flask_appbuilder.basemanager import BaseManager
    from flask_appbuilder.baseviews import BaseView, AbstractViewApi
    from flask_appbuilder.security.manager import BaseSecurityManager

log = logging.getLogger(__name__)


DynamicImportType = Union[
    Type["BaseManager"],
    Type["BaseView"],
    Type["BaseSecurityManager"],
    Type[Menu],
    Type["AbstractViewApi"],
]


def dynamic_class_import(class_path: str) -> Optional[DynamicImportType]:
    """
    Will dynamically import a class from a string path
    :param class_path: string with class path
    :return: class
    """
    # Split first occurrence of path
    try:
        tmp = class_path.split(".")
        module_path = ".".join(tmp[0:-1])
        package = __import__(module_path)
        return reduce(getattr, tmp[1:], package)  # type: ignore
    except Exception as e:
        log.exception(e)
        log.error(LOGMSG_ERR_FAB_ADDON_IMPORT, class_path, e)
        return None


class AppBuilder:
    """
    This is the base class for all the framework.
    This is where you will register all your views and create the menu structure.
    Will hold your flask app object, all your views, and security classes.

    initialize your application like this for SQLAlchemy::

        from flask import Flask
        from flask_appbuilder import AppBuilder

        app = Flask(__name__)
        app.config.from_object('config')
        appbuilder = AppBuilder(app)

    When using MongoEngine::

        from flask import Flask
        from flask_appbuilder import AppBuilder
        from flask_appbuilder.security.mongoengine.manager import SecurityManager
        from flask_mongoengine import MongoEngine

        app = Flask(__name__)
        app.config.from_object('config')
        dbmongo = MongoEngine(app)
        appbuilder = AppBuilder(app, security_manager_class=SecurityManager)

    You can also create everything as an application factory.
    """

    security_manager_class = None

    template_filters = None

    def __init__(
        self,
        app: Optional[Flask] = None,
        menu: Optional[Menu] = None,
        indexview: Optional[Type["AbstractViewApi"]] = None,
        base_template: str = "appbuilder/baselayout.html",
        static_folder: str = "static/appbuilder",
        static_url_path: str = "/appbuilder",
        security_manager_class: Optional[Type["BaseSecurityManager"]] = None,
        update_perms: bool = True,
    ) -> None:
        """
        AppBuilder init

        :param app:
            The flask app object
        :param menu:
            optional, a previous contructed menu
        :param indexview:
            optional, your customized indexview
        :param static_folder:
            optional, your override for the global static folder
        :param static_url_path:
            optional, your override for the global static url path
        :param security_manager_class:
            optional, pass your own security manager class
        :param update_perms:
            optional, update permissions flag (Boolean) you can use
            FAB_UPDATE_PERMS config key also
        """
        self.baseviews: List[Union[Type["AbstractViewApi"], "AbstractViewApi"]] = []

        # temporary list that hold addon_managers config key
        self._addon_managers: List[str] = []
        # dict with addon name has key and instantiated class has value
        self.addon_managers: Dict[str, Any] = {}
        self.menu = menu
        self.base_template = base_template
        self.security_manager_class = security_manager_class
        self.indexview = indexview
        self.static_folder = static_folder
        self.static_url_path = static_url_path
        self.update_perms = update_perms

        # Security Manager Class
        self.sm: BaseSecurityManager = None  # type: ignore
        # Babel Manager Class
        self.bm: BabelManager = None  # type: ignore
        self.openapi_manager: OpenApiManager = None  # type: ignore
        self.menuapi_manager: MenuApiManager = None  # type: ignore

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """
        Will initialize the Flask app, supporting the app factory pattern.

        :param app:
        :param session: The SQLAlchemy session

        """
        app.config.setdefault("APP_NAME", "F.A.B.")
        app.config.setdefault("APP_THEME", "")
        app.config.setdefault("APP_ICON", "")
        app.config.setdefault("LANGUAGES", {"en": {"flag": "gb", "name": "English"}})
        app.config.setdefault("ADDON_MANAGERS", [])
        app.config.setdefault("RATELIMIT_ENABLED", False)
        app.config.setdefault("FAB_API_MAX_PAGE_SIZE", 100)
        app.config.setdefault("FAB_BASE_TEMPLATE", self.base_template)
        app.config.setdefault("FAB_STATIC_FOLDER", self.static_folder)
        app.config.setdefault("FAB_STATIC_URL_PATH", self.static_url_path)

        self._init_extension(app)
        # init flask-sqlalchemy if needed
        if "sqlalchemy" not in app.extensions:
            self.session.remove()
            log.debug("Base: SQLAlchemy not in app.extensions")
            db.init_app(app)
        self.base_template = app.config.get("FAB_BASE_TEMPLATE", self.base_template)
        self.static_folder = app.config.get("FAB_STATIC_FOLDER", self.static_folder)
        self.static_url_path = app.config.get(
            "FAB_STATIC_URL_PATH", self.static_url_path
        )
        _index_view = app.config.get("FAB_INDEX_VIEW", None)
        if _index_view:
            self.indexview = dynamic_class_import(_index_view)  # type: ignore
        else:
            self.indexview = self.indexview or IndexView

        _menu = app.config.get("FAB_MENU", None)

        # Setup Menu
        if _menu is not None:
            menu = dynamic_class_import(_menu)
            if menu is not None and issubclass(menu, Menu):
                self.menu = menu()
        else:
            self.menu = self.menu or Menu()

        if self.update_perms:  # default is True, if False takes precedence from config
            self.update_perms = app.config.get("FAB_UPDATE_PERMS", True)
        _security_manager_class_name = app.config.get(
            "FAB_SECURITY_MANAGER_CLASS", None
        )
        if _security_manager_class_name is not None:
            security_manager_class = dynamic_class_import(_security_manager_class_name)
            self.security_manager_class = cast(
                Type["BaseSecurityManager"], security_manager_class
            )
        if self.security_manager_class is None:
            from flask_appbuilder.security.sqla.manager import SecurityManager

            self.security_manager_class = SecurityManager

        self._addon_managers = app.config["ADDON_MANAGERS"]
        self.sm = self.security_manager_class(self)
        self.bm = BabelManager(self)
        self.openapi_manager = OpenApiManager(self)
        self.menuapi_manager = MenuApiManager(self)
        self._add_global_static()
        self._add_global_filters()
        app.before_request(self.sm.before_request)
        self._add_admin_views()
        self._add_addon_views()
        self._add_menu_permissions()

    def _init_extension(self, app: Flask) -> None:
        app.appbuilder = self
        if "appbuilder" in app.extensions:
            raise RuntimeError(
                "A 'Flask-AppBuilder' instance has"
                " already been registered on this Flask app."
            )
        app.extensions["appbuilder"] = self

    def post_init(self) -> None:
        for baseview in self.baseviews:
            # instantiate the views and add session
            baseview = self._check_and_init(baseview)
            # Register the views has blueprints
            if baseview.__class__.__name__ not in current_app.blueprints.keys():
                self.register_blueprint(baseview)
            # Add missing permissions where needed
        self.add_permissions()

    @property
    def app(self) -> Flask:
        log.warning(
            "appbuilder.app will be deprecated in future versions, "
            "use current_app instead"
        )
        return current_app

    @property
    def session(self) -> SessionBase:
        """
        Get the current sqlalchemy session.

        :return: SQLAlchemy Session
        """
        return db.session

    @property
    def app_name(self) -> str:
        """
        Get the App name

        :return: String with app name
        """
        return current_app.config["APP_NAME"]

    @property
    def app_theme(self) -> str:
        """
        Get the App theme name

        :return: String app theme name
        """
        return current_app.config["APP_THEME"]

    @property
    def app_icon(self) -> str:
        """
        Get the App icon location

        :return: String with relative app icon location
        """
        return current_app.config["APP_ICON"]

    @property
    def languages(self) -> Dict[str, Any]:
        return current_app.config["LANGUAGES"]

    @property
    def version(self) -> str:
        """
        Get the current F.A.B. version

        :return: String with the current F.A.B. version
        """
        return __version__

    def _add_global_filters(self) -> None:
        self.template_filters = TemplateFilters(current_app, self.sm)

    def _add_global_static(self) -> None:
        bp = Blueprint(
            "appbuilder",
            __name__,
            url_prefix="/static",
            template_folder="templates",
            static_folder=self.static_folder,
            static_url_path=self.static_url_path,
        )
        current_app.register_blueprint(bp)

    def _add_admin_views(self) -> None:
        """
        Registers indexview, utilview (back function), babel views and Security views.
        """
        if self.indexview:
            self._indexview = self.add_view_no_menu(self.indexview)
        self.add_view_no_menu(UtilView)
        self.bm.register_views()
        self.sm.register_views()
        self.openapi_manager.register_views()
        self.menuapi_manager.register_views()

    def _add_addon_views(self) -> None:
        """
        Registers declared addon's
        """
        for addon in self._addon_managers:
            addon_class_ = dynamic_class_import(addon)
            addon_class = cast(Type["BaseManager"], addon_class_)
            if addon_class:
                # Instantiate manager with appbuilder (self)
                inst_addon_class: "BaseManager" = addon_class(self)
                try:
                    inst_addon_class.pre_process()
                    inst_addon_class.register_views()
                    inst_addon_class.post_process()
                    self.addon_managers[addon] = inst_addon_class
                    log.info(LOGMSG_INF_FAB_ADDON_ADDED, addon)
                except Exception as e:
                    log.exception(e)
                    log.error(LOGMSG_ERR_FAB_ADDON_PROCESS, addon, e)

    def _check_and_init(
        self, baseview: Union[Type["AbstractViewApi"], "AbstractViewApi"]
    ) -> "AbstractViewApi":
        if isinstance(baseview, type):
            baseview = baseview()
        return baseview

    def add_view(
        self,
        baseview: Union[Type["AbstractViewApi"], "AbstractViewApi"],
        name: str,
        href: str = "",
        icon: str = "",
        label: str = "",
        category: str = "",
        category_icon: str = "",
        category_label: str = "",
        menu_cond: Optional[Callable[..., bool]] = None,
    ) -> "AbstractViewApi":
        """
        Add your views associated with menus using this method.

        :param baseview:
            A BaseView type class instantiated or not.
            This method will instantiate the class for you if needed.
        :param name:
            The string name that identifies the menu.
        :param href:
            Override the generated href for the menu.
            You can use an url string or an endpoint name
            if non provided default_view from view will be set as href.
        :param icon:
            Font-Awesome icon name, optional.
        :param label:
            The label that will be displayed on the menu,
            if absent param name will be used
        :param category:
            The menu category where the menu will be included,
            if non provided the view will be acessible as a top menu.
        :param category_icon:
            Font-Awesome icon name for the category, optional.
        :param category_label:
            The label that will be displayed on the menu,
            if absent param name will be used
        :param menu_cond:
            If a callable, :code:`menu_cond` will be invoked when
            constructing the menu items. If it returns :code:`True`,
            then this link will be a part of the menu. Otherwise, it
            will not be included in the menu items. Defaults to
            :code:`None`, meaning the item will always be present.

        Examples::

            appbuilder = AppBuilder(app, db)
            # Register a view, rendering a top menu without icon.
            appbuilder.add_view(MyModelView(), "My View")
            # or not instantiated
            appbuilder.add_view(MyModelView, "My View")
            # Register a view, a submenu "Other View" from "Other" with a phone icon.
            appbuilder.add_view(
                MyOtherModelView,
                "Other View",
                icon='fa-phone',
                category="Others"
            )
            # Register a view, with category icon and translation.
            appbuilder.add_view(
                YetOtherModelView,
                "Other View",
                icon='fa-phone',
                label=_('Other View'),
                category="Others",
                category_icon='fa-envelop',
                category_label=_('Other View')
            )
            # Register a view whose menu item will be conditionally displayed
            appbuilder.add_view(
                YourFeatureView,
                "Your Feature",
                icon='fa-feature',
                label=_('Your Feature'),
                menu_cond=lambda: is_feature_enabled("your-feature"),
            )
            # Add a link
            appbuilder.add_link("google", href="www.google.com", icon = "fa-google-plus")
        """
        baseview = self._check_and_init(baseview)
        log.info(LOGMSG_INF_FAB_ADD_VIEW, baseview.__class__.__name__, name)

        if not self._view_exists(baseview):
            baseview.appbuilder = self
            self.baseviews.append(baseview)
            self._process_inner_views()
            self.register_blueprint(baseview)
            self._add_permission(baseview)
            self.add_limits(baseview)
        self.add_link(
            name=name,
            href=href,
            icon=icon,
            label=label,
            category=category,
            category_icon=category_icon,
            category_label=category_label,
            baseview=baseview,
            cond=menu_cond,
        )
        return baseview

    def add_link(
        self,
        name: str,
        href: str,
        icon: str = "",
        label: str = "",
        category: str = "",
        category_icon: str = "",
        category_label: str = "",
        baseview: Optional["AbstractViewApi"] = None,
        cond: Optional[Callable[..., bool]] = None,
    ) -> None:
        """
        Add your own links to menu using this method

        :param baseview:
        :param name:
            The string name that identifies the menu.
        :param href:
            Override the generated href for the menu.
            You can use an url string or an endpoint name
        :param icon:
            Font-Awesome icon name, optional.
        :param label:
            The label that will be displayed on the menu,
            if absent param name will be used
        :param category:
            The menu category where the menu will be included,
            if non provided the view will be accessible as a top menu.
        :param category_icon:
            Font-Awesome icon name for the category, optional.
        :param category_label:
            The label that will be displayed on the menu,
            if absent param name will be used
        :param cond:
            If a callable, :code:`cond` will be invoked when
            constructing the menu items. If it returns :code:`True`,
            then this link will be a part of the menu. Otherwise, it
            will not be included in the menu items. Defaults to
            :code:`None`, meaning the item will always be present.
        """
        if self.menu is None:
            return
        self.menu.add_link(
            name=name,
            href=href,
            icon=icon,
            label=label,
            category=category,
            category_icon=category_icon,
            category_label=category_label,
            baseview=baseview,
            cond=cond,
        )
        self._add_permissions_menu(name)
        if category:
            self._add_permissions_menu(category)

    def add_separator(
        self, category: str, cond: Optional[Callable[..., bool]] = None
    ) -> None:
        """
        Add a separator to the menu, you will sequentially create the menu

        :param category:
            The menu category where the separator will be included.
        :param cond:
            If a callable, :code:`cond` will be invoked when
            constructing the menu items. If it returns :code:`True`,
            then this separator will be a part of the menu. Otherwise,
            it will not be included in the menu items. Defaults to
            :code:`None`, meaning the separator will always be present.
        """
        if self.menu is None:
            return
        self.menu.add_separator(category, cond=cond)

    def add_view_no_menu(
        self,
        baseview: Union[Type["AbstractViewApi"], "AbstractViewApi"],
        endpoint: Optional[str] = None,
        static_folder: Optional[str] = None,
    ) -> "AbstractViewApi":
        """
        Add your views without creating a menu.

        :param baseview:
            A BaseView type class instantiated.
        :param endpoint: The endpoint path for the Flask blueprint
        :param static_folder: The static folder for the Flask blueprint

        """
        baseview = self._check_and_init(baseview)
        log.info(LOGMSG_INF_FAB_ADD_VIEW, baseview.__class__.__name__, "")

        if not self._view_exists(baseview):
            baseview.appbuilder = self
            self.baseviews.append(baseview)
            self._process_inner_views()
            self.register_blueprint(
                baseview, endpoint=endpoint, static_folder=static_folder
            )
            self._add_permission(baseview)
            self.add_limits(baseview)
        else:
            log.warning(LOGMSG_WAR_FAB_VIEW_EXISTS, baseview.__class__.__name__)
        return baseview

    def add_api(self, baseview: Type["AbstractViewApi"]) -> "AbstractViewApi":
        """
        Add a BaseApi class or child to AppBuilder

        :param baseview: A BaseApi type class
        :return: The instantiated base view
        """
        return self.add_view_no_menu(baseview)

    def security_cleanup(self) -> None:
        """
        This method is useful if you have changed
        the name of your menus or classes,
        changing them will leave behind permissions
        that are not associated with anything.

        You can use it always or just sometimes to
        perform a security cleanup. Warning this will delete any permission
        that is no longer part of any registered view or menu.

        Remember invoke ONLY AFTER YOU HAVE REGISTERED ALL VIEWS
        """
        self.sm.security_cleanup(self.baseviews, self.menu)

    def security_converge(self, dry: bool = False) -> Dict[str, Any]:
        """
        This method is useful when you use:

        - `class_permission_name`
        - `previous_class_permission_name`
        - `method_permission_name`
        - `previous_method_permission_name`

        migrates all permissions to the new names on all the Roles

        :param dry: If True will not change DB
        :return: Dict with all computed necessary operations
        """
        if self.menu is None:
            return {}
        return self.sm.security_converge(self.baseviews, self.menu.menu, dry)

    def get_url_for_login_with(self, next_url: str | None = None) -> str:
        if self.sm.auth_view is None:
            return ""
        return url_for("%s.%s" % (self.sm.auth_view.endpoint, "login"), next=next_url)

    @property
    def get_url_for_login(self) -> str:
        if self.sm.auth_view is None:
            return ""
        return url_for("%s.%s" % (self.sm.auth_view.endpoint, "login"))

    @property
    def get_url_for_logout(self) -> str:
        if self.sm.auth_view is None:
            return ""
        return url_for("%s.%s" % (self.sm.auth_view.endpoint, "logout"))

    @property
    def get_url_for_index(self) -> str:
        if self._indexview is None:
            return ""
        return url_for(
            "%s.%s" % (self._indexview.endpoint, self._indexview.default_view)
        )

    @property
    def get_url_for_userinfo(self) -> str:
        if self.sm.user_view is None:
            return ""
        return url_for("%s.%s" % (self.sm.user_view.endpoint, "userinfo"))

    def get_url_for_locale(self, lang: str) -> str:
        if self.bm.locale_view is None:
            return ""
        return url_for(
            "%s.%s" % (self.bm.locale_view.endpoint, self.bm.locale_view.default_view),
            locale=lang,
        )

    def add_limits(self, baseview: "AbstractViewApi") -> None:
        if hasattr(baseview, "limits"):
            self.sm.add_limit_view(baseview)

    def add_permissions(self, update_perms: bool = False) -> None:
        from flask_appbuilder.baseviews import AbstractViewApi

        if self.update_perms or update_perms:
            for baseview in self.baseviews:
                baseview = cast(AbstractViewApi, baseview)
                self._add_permission(baseview, update_perms=update_perms)
            self._add_menu_permissions(update_perms=update_perms)

    def _add_permission(
        self, baseview: "AbstractViewApi", update_perms: bool = False
    ) -> None:
        if self.update_perms or update_perms:
            try:
                self.sm.add_permissions_view(
                    baseview.base_permissions, baseview.class_permission_name
                )
            except Exception as e:
                log.exception(e)
                log.error(LOGMSG_ERR_FAB_ADD_PERMISSION_VIEW, e)

    def _add_permissions_menu(self, name: str, update_perms: bool = False) -> None:
        if self.update_perms or update_perms:
            try:
                self.sm.add_permissions_menu(name)
            except Exception as e:
                log.exception(e)
                log.error(LOGMSG_ERR_FAB_ADD_PERMISSION_MENU, e)

    def _add_menu_permissions(self, update_perms: bool = False) -> None:
        if self.menu is None:
            return
        if self.update_perms or update_perms:
            for category in self.menu.get_list():
                self._add_permissions_menu(category.name, update_perms=update_perms)
                for item in category.childs:
                    # don't add permission for menu separator
                    if item.name != "-":
                        self._add_permissions_menu(item.name, update_perms=update_perms)

    def register_blueprint(
        self,
        baseview: "AbstractViewApi",
        endpoint: Optional[str] = None,
        static_folder: Optional[str] = None,
    ) -> None:
        current_app.register_blueprint(
            baseview.create_blueprint(
                self, endpoint=endpoint, static_folder=static_folder
            )
        )

    def _view_exists(self, view: "AbstractViewApi") -> bool:
        for baseview in self.baseviews:
            if baseview.__class__ == view.__class__:
                return True
        return False

    def _process_inner_views(self) -> None:
        from flask_appbuilder.baseviews import AbstractViewApi

        for view in self.baseviews:
            view = cast(AbstractViewApi, view)
            for inner_class in view.get_uninit_inner_views():
                for v in self.baseviews:
                    if (
                        isinstance(v, inner_class)
                        and v not in view.get_init_inner_views()
                    ):
                        view.get_init_inner_views().append(v)
