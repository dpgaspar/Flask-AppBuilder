from flask import current_app, url_for

from .api import BaseApi, expose
from .basemanager import BaseManager
from .security.decorators import permission_name, protect


class MenuItem(object):
    name = ""
    href = ""
    icon = ""
    label = ""
    baseview = None
    childs = []

    def __init__(self, name, href="", icon="", label="", childs=None, baseview=None):
        self.name = name
        self.href = href
        self.icon = icon
        self.label = label
        if self.childs:
            self.childs = childs
        else:
            self.childs = []
        self.baseview = baseview

    def get_url(self):
        if not self.href:
            if not self.baseview:
                return ""
            else:
                return url_for(
                    "{}.{}".format(self.baseview.endpoint, self.baseview.default_view)
                )
        else:
            try:
                return url_for(self.href)
            except Exception:
                return self.href

    def __repr__(self):
        return self.name


class Menu(object):
    menu = None

    def __init__(self, reverse=True, extra_classes=""):
        self.menu = []
        if reverse:
            extra_classes = extra_classes + "navbar-inverse"
        self.extra_classes = extra_classes

    @property
    def reverse(self):
        return "navbar-inverse" in self.extra_classes

    def get_list(self):
        return self.menu

    def get_data(self, menu=None):
        menu = menu or self.menu
        ret_list = []

        for i, item in enumerate(menu):
            if item.name == '-' and not i == len(menu) - 1:
                ret_list.append('-')
            elif not current_app.appbuilder.sm.has_access("menu_access", item.name):
                continue
            elif item.childs:
                ret_list.append({
                    "name": item.name,
                    "icon": item.icon,
                    "label": str(item.label),
                    "childs": self.get_data(menu=item.childs)
                })
            else:
                ret_list.append({
                    "name": item.name,
                    "icon": item.icon,
                    "label": str(item.label),
                    "url": item.get_url()
                })
        return ret_list

    def find(self, name, menu=None):
        """
            Finds a menu item by name and returns it.

            :param name:
                The menu item name.
        """
        menu = menu or self.menu
        for i in menu:
            if i.name == name:
                return i
            else:
                if i.childs:
                    ret_item = self.find(name, menu=i.childs)
                    if ret_item:
                        return ret_item

    def add_category(self, category, icon="", label="", parent_category=""):
        label = label or category
        if parent_category == "":
            self.menu.append(MenuItem(name=category, icon=icon, label=label))
        else:
            self.find(category).childs.append(
                MenuItem(name=category, icon=icon, label=label)
            )

    def add_link(
        self,
        name,
        href="",
        icon="",
        label="",
        category="",
        category_icon="",
        category_label="",
        baseview=None,
    ):
        label = label or name
        category_label = category_label or category
        if category == "":
            self.menu.append(
                MenuItem(
                    name=name, href=href, icon=icon, label=label, baseview=baseview
                )
            )
        else:
            menu_item = self.find(category)
            if menu_item:
                new_menu_item = MenuItem(
                    name=name, href=href, icon=icon, label=label, baseview=baseview
                )
                menu_item.childs.append(new_menu_item)
            else:
                self.add_category(
                    category=category, icon=category_icon, label=category_label
                )
                new_menu_item = MenuItem(
                    name=name, href=href, icon=icon, label=label, baseview=baseview
                )
                self.find(category).childs.append(new_menu_item)

    def add_separator(self, category=""):
        menu_item = self.find(category)
        if menu_item:
            menu_item.childs.append(MenuItem("-"))
        else:
            raise Exception(
                "Menu separator does not have correct category {}".format(category)
            )


class MenuApi(BaseApi):
    resource_name = "menu"

    @expose('/', methods=["GET"])
    @protect(allow_browser_login=True)
    @permission_name('get')
    def get_menu_data(self):
        """An endpoint for retreiving the menu.
        ---
        get:
          responses:
            200:
              description: Get menu data
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      result:
                        type: array
                        items:
                          oneOf:
                            Seperator:
                              type: string
                              enum:
                              - '-'
                            MenuObject:
                              type: object
                              properties:
                                name:
                                  type: string
                                label:
                                  type: string
                                icon:
                                  type: string
                                url:
                                  type: string
                                childs:
                                  $ref: \
        '#/paths/menu/data/get/reponses/200/content/application/json/schema/properties/result'
                              required:
                                - name
                                - url

            401:
              $ref: '#/components/responses/401'
        """
        return self.response(200, result=current_app.appbuilder.menu.get_data())


class MenuApiManager(BaseManager):
    def register_views(self):
        if self.appbuilder.app.config.get('FAB_ADD_MENU_API', True):
            self.appbuilder.add_api(MenuApi)
