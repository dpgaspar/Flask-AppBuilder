from flask import g, request, current_app
from flask.ext.login import current_user
from flask import render_template, flash, redirect,url_for
from models import is_item_public

def has_access(f):
    """
        Use this decorator to allow access only to security 
        defined permissions
    """
    def wrap(self, *args, **kwargs):
        if current_user.is_authenticated():
            if g.user.has_permission_on_view("can_" + f.__name__, self.__class__.__name__):
                return f(self, *args, **kwargs)
            else:
                flash("Access is Denied %s %s" % (f.__name__, self.__class__.__name__),"danger")
        else:
            if is_item_public("can_" + f.__name__, self.__class__.__name__):
                return f(self, *args, **kwargs)
            else:
                flash("Access is Denied %s %s" % (f.__name__, self.__class__.__name__),"danger")
        return redirect(url_for("authview.login"))
    return wrap

    
