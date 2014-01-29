from flask import url_for


class MenuItem(object):

    name = ""
    baseview = None
    href = ""
    icon = ""
    childs = []

    def __init__(self, name, href="", icon="", childs=[], baseview = None):
        self.name = name
        self.href = href
        self.icon = icon
        if (self.childs):
            self.childs = childs
        else: self.childs = []
        self.baseview = baseview

    def get_url(self):
        if not self.href:
            if not self.baseview:
                return ""
            else:
                return url_for('%s.%s' % (self.baseview.endpoint, self.baseview.default_view))
        else:
            return self.href

    def __repr__(self):
        return self.name

class Menu(object):

    menu = None
    reverse = True
    
    def __init__(self, reverse=True):
        self.menu = []
        self.reverse = reverse

    def get_list(self):
        return self.menu

    # Mal programado para rever
    def find_category(self, category):
        for i in self.menu:
            if i.name == category:
                return i
            else:
                for j in i.childs:
                    if j.name == category:
                        return j


    def add_category(self, category, icon="", parent_category=""):
        if parent_category == "":
            self.menu.append(MenuItem(name=category, icon = icon))
        else:
            self.find_category(category).childs.append(MenuItem(name=category, icon = icon))
        

    def add_link(self, name, href="", icon="", category="", baseview = None):
        if category == "":
            self.menu.append(MenuItem(name=name, href=href, icon = icon, baseview=baseview))
        else:
            menu_item = self.find_category(category)
            if menu_item:
                menu_item.childs.append(MenuItem(name=name, href=href, icon = icon, baseview = baseview))
            else:
                self.add_category(category=category)
                self.find_category(category).childs.append(MenuItem(name=name, 
                                        href=href, icon = icon, baseview = baseview))
        

    def add_separator(self, category=""):
        self.find_category(category).childs.append(MenuItem("-"))
        
    def debug(self):
        for i in self.menu:
            print i
            for j in i.childs:
                print "-", j

