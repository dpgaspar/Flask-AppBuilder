class SecProxy(object)

    session = None

    def __init__(self, session):
        self.session = session
    
  
    def is_menu_public(item):
        """
            Check if menu item has public permissions
    
            param item:
                menu item
        """
        role_public = current_app.config['AUTH_ROLE_PUBLIC']
        role = self.session.query(Role).filter_by(name = role_public).first()
        lst = role.permissions
        if lst:
            for i in lst:
                if item == i.view_menu.name:
                    return  True
            return False
        else: return False

    def is_item_public(permission_name, view_name):
        """
            Check if view has public permissions
    
            param permission_name:
                the permission: can_show, can_edit...
            param view_name:
                the name of the class view (child of BaseView)
        """
        role_public = current_app.config['AUTH_ROLE_PUBLIC']
        role = self.session.query(Role).filter_by(name = role_public).first()
        lst = role.permissions
        if lst:
            for i in lst:
                if (view_name == i.view_menu.name) and (permission_name == i.permission.name):
                    return True
            return False
        else: return False
    
    def add_permission(self, name):
        """
            Adds a permission to the backend
            param name:
                name of the permission to add: 'can_add','can_edit' etc...
        """
        perm = self.session.query(Permission).filter_by(name = name).first()
        if perm == None:
            perm = Permission()
            perm.name = name
            self.session.add(perm)
            self.session.commit()
            return perm
        return perm
        
        
    def add_view_menu(self, name):
        view_menu = self.session.query(ViewMenu).filter_by(name = name).first()
        if view_menu == None:
            view_menu = ViewMenu()
            view_menu.name = name
            self.session.add(view_menu)
            self.session.commit()
            return view_menu
        return view_menu
