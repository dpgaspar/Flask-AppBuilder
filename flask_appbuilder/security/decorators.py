from flask import flash, redirect,url_for,g
from functools


def has_access(f):
    """
        Use this decorator to allow access only to security
        defined permissions, use it only on BaseView classes.
    """

    def wraps(self, *args, **kwargs):
        permission_str = "can_" + f.__name__
        if self.appbuilder.sm.has_access(permission_str, self.__class__.__name__):
            return f(self, *args, **kwargs)
        else:
            flash("Access is Denied %s %s" % (f.__name__, self.__class__.__name__), "danger")
        return redirect(url_for(self.appbuilder.sm.auth_view.__class__.__name__ + ".login"))
    return wraps


def permission_name(name):
    """
        Use this decorator to override the name of the permission.
        has_access will use the methods name has the permission name
        if you want to override this add this decorator to your methods.
        This is useful if you want to aggregate methods to permissions

        It will add and '_permission_name' attribute to your method
        that will be inspected by BaseView to collect your view's
        permissions.

        :param name:
            The name of the permission to override
    """
    def wrap(f):
        f._permission_name = name
        return functools.update_wrapper(wrap, f)
    return wrap
    
