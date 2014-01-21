from flask.ext.login import current_user
from flask import flash, redirect,url_for,g

def has_access(f):
        """
            Use this decorator to allow access only to security 
            defined permissions, use it only on BaseView classes.
        """
 
        def wraps(self, *args, **kwargs):
            if self.baseapp.sm.has_access("can_" + f.__name__, self.__class__.__name__):
                return f(self, *args, **kwargs)
            else:
                flash("Access is Denied %s %s" % (f.__name__, self.__class__.__name__),"danger")
            return redirect(url_for(self.baseapp.sm.auth_view.__class__.__name__+ ".login"))
        return wraps
