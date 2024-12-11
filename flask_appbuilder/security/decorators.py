import functools
import logging
from typing import Callable, List, Optional, TypeVar, Union

from flask import (
    current_app,
    flash,
    jsonify,
    make_response,
    redirect,
    request,
    Response,
    url_for,
)
from flask_appbuilder._compat import as_unicode
from flask_appbuilder.const import (
    FLAMSG_ERR_SEC_ACCESS_DENIED,
    LOGMSG_ERR_SEC_ACCESS_DENIED,
    PERMISSION_PREFIX,
)
from flask_appbuilder.utils.limit import Limit
from flask_jwt_extended import verify_jwt_in_request
from flask_limiter.wrappers import RequestLimit
from flask_login import current_user
from typing_extensions import ParamSpec

log = logging.getLogger(__name__)

R = TypeVar("R")
P = ParamSpec("P")


def no_cache(view: Callable[..., Response]) -> Callable[..., Response]:
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs) -> Response:
        response = make_response(view(*args, **kwargs))
        response.headers[
            "Cache-Control"
        ] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    return wrapped_view


def response_unauthorized_mvc(status_code: int) -> Response:
    response = make_response(
        jsonify({"message": str(FLAMSG_ERR_SEC_ACCESS_DENIED), "severity": "danger"}),
        status_code,
    )
    response.headers["Content-Type"] = "application/json"
    return response


def protect(allow_browser_login=False):
    """
    Use this decorator to enable granular security permissions
    to your API methods (BaseApi and child classes).
    Permissions will be associated to a role, and roles are associated to users.

    allow_browser_login will accept signed cookies obtained from the normal MVC app::

        class MyApi(BaseApi):
            @expose('/dosonmething', methods=['GET'])
            @protect(allow_browser_login=True)
            @safe
            def do_something(self):
                ....

            @expose('/dosonmethingelse', methods=['GET'])
            @protect()
            @safe
            def do_something_else(self):
                ....

    By default the permission's name is the methods name.
    """

    def _protect(f):
        if hasattr(f, "_permission_name"):
            permission_str = f._permission_name
        else:
            permission_str = f.__name__

        def wraps(self, *args, **kwargs):
            # Apply method permission name override if exists
            permission_str = f"{PERMISSION_PREFIX}{f._permission_name}"
            if self.method_permission_name:
                _permission_name = self.method_permission_name.get(f.__name__)
                if _permission_name:
                    permission_str = f"{PERMISSION_PREFIX}{_permission_name}"
            class_permission_name = self.class_permission_name
            # Check if permission is allowed on the class
            if permission_str not in self.base_permissions:
                return self.response_403()
            # Check if the resource is public
            if current_app.appbuilder.sm.is_item_public(
                permission_str, class_permission_name
            ):
                return f(self, *args, **kwargs)
            # if no browser login then verify JWT
            if not (self.allow_browser_login or allow_browser_login):
                verify_jwt_in_request()
            # Verify resource access
            if current_app.appbuilder.sm.has_access(
                permission_str, class_permission_name
            ):
                return f(self, *args, **kwargs)
            # If browser login?
            elif self.allow_browser_login or allow_browser_login:
                # no session cookie (but we allow it), then try JWT
                if not current_user.is_authenticated:
                    verify_jwt_in_request()
                if current_app.appbuilder.sm.has_access(
                    permission_str, class_permission_name
                ):
                    return f(self, *args, **kwargs)
            log.warning(
                LOGMSG_ERR_SEC_ACCESS_DENIED, permission_str, class_permission_name
            )
            return self.response_403()

        f._permission_name = permission_str
        return functools.update_wrapper(wraps, f)

    return _protect


def has_access(f):
    """
    Use this decorator to enable granular security permissions to your methods.
    Permissions will be associated to a role, and roles are associated to users.

    By default the permission's name is the methods name.
    """
    if hasattr(f, "_permission_name"):
        permission_str = f._permission_name
    else:
        permission_str = f.__name__

    def wraps(self, *args, **kwargs):
        permission_str = f"{PERMISSION_PREFIX}{f._permission_name}"
        if self.method_permission_name:
            _permission_name = self.method_permission_name.get(f.__name__)
            if _permission_name:
                permission_str = f"{PERMISSION_PREFIX}{_permission_name}"
        if permission_str in self.base_permissions and self.appbuilder.sm.has_access(
            permission_str, self.class_permission_name
        ):
            return f(self, *args, **kwargs)
        else:
            log.warning(
                LOGMSG_ERR_SEC_ACCESS_DENIED, permission_str, self.__class__.__name__
            )
            flash(as_unicode(FLAMSG_ERR_SEC_ACCESS_DENIED), "danger")
        return redirect(
            url_for(
                self.appbuilder.sm.auth_view.__class__.__name__ + ".login",
                next=request.url,
            )
        )

    f._permission_name = permission_str
    return functools.update_wrapper(wraps, f)


def has_access_api(f):
    """
    Use this decorator to enable granular security permissions to your API methods.
    Permissions will be associated to a role, and roles are associated to users.

    By default the permission's name is the methods name.

    this will return a message and HTTP 403 is case of unauthorized access.
    """
    if hasattr(f, "_permission_name"):
        permission_str = f._permission_name
    else:
        permission_str = f.__name__

    def wraps(self, *args, **kwargs):
        permission_str = f"{PERMISSION_PREFIX}{f._permission_name}"
        if self.method_permission_name:
            _permission_name = self.method_permission_name.get(f.__name__)
            if _permission_name:
                permission_str = f"{PERMISSION_PREFIX}{_permission_name}"
        if permission_str in self.base_permissions and self.appbuilder.sm.has_access(
            permission_str, self.class_permission_name
        ):
            return f(self, *args, **kwargs)
        else:
            log.warning(
                LOGMSG_ERR_SEC_ACCESS_DENIED, permission_str, self.__class__.__name__
            )
            if not current_user.is_authenticated:
                return response_unauthorized_mvc(401)
            return response_unauthorized_mvc(403)

    f._permission_name = permission_str
    return functools.update_wrapper(wraps, f)


def permission_name(name):
    """
    Use this decorator to override the name of the permission.
    has_access will use the methods name has the permission name
    if you want to override this add this decorator to your methods.
    This is useful if you want to aggregate methods to permissions

    It will add '_permission_name' attribute to your method
    that will be inspected by BaseView to collect your view's
    permissions.

    Note that you should use @has_access to execute after @permission_name
    like on the following example.

    Use it like this to aggregate permissions for your methods::

        class MyModelView(ModelView):
            datamodel = SQLAInterface(MyModel)

            @has_access
            @permission_name('GeneralXPTO_Permission')
            @expose(url='/xpto')
            def xpto(self):
                return "Your on xpto"

            @has_access
            @permission_name('GeneralXPTO_Permission')
            @expose(url='/xpto2')
            def xpto2(self):
                return "Your on xpto2"


    :param name:
        The name of the permission to override
    """

    def wraps(f):
        f._permission_name = name
        return f

    return wraps


def limit(
    limit_value: Union[str, Callable[[], str]],
    key_func: Optional[Callable[[], str]] = None,
    per_method: bool = False,
    methods: Optional[List[str]] = None,
    error_message: Optional[str] = None,
    exempt_when: Optional[Callable[[], bool]] = None,
    override_defaults: bool = True,
    deduct_when: Optional[Callable[[Response], bool]] = None,
    on_breach: Optional[Callable[[RequestLimit], Optional[Response]]] = None,
    cost: Union[int, Callable[[], int]] = 1,
):
    """
    Decorator to be used for rate limiting individual routes or blueprints.

    :param limit_value: rate limit string or a callable that returns a
     string. :ref:`ratelimit-string` for more details.
    :param key_func: function/lambda to extract the unique
     identifier for the rate limit. defaults to remote address of the
     request.
    :param per_method: whether the limit is sub categorized into the
     http method of the request.
    :param methods: if specified, only the methods in this list will
     be rate limited (default: ``None``).
    :param error_message: string (or callable that returns one) to override
     the error message used in the response.
    :param exempt_when: function/lambda used to decide if the rate
     limit should skipped.
    :param override_defaults:  whether the decorated limit overrides
     the default limits (Default: ``True``).

     .. note:: When used with a :class:`~BaseView` the meaning
        of the parameter extends to any parents the blueprint instance is
        registered under. For more details see :ref:`recipes:nested blueprints`

    :param deduct_when: a function that receives the current
     :class:`flask.Response` object and returns True/False to decide if a
     deduction should be done from the rate limit
    :param on_breach: a function that will be called when this limit
     is breached. If the function returns an instance of :class:`flask.Response`
     that will be the response embedded into the :exc:`RateLimitExceeded` exception
     raised.
    :param cost: The cost of a hit or a function that
     takes no parameters and returns the cost as an integer (Default: ``1``).
    """

    def wraps(f: Callable[P, R]) -> Callable[P, R]:
        _limit = Limit(
            limit_value=limit_value,
            key_func=key_func,
            per_method=per_method,
            methods=methods,
            error_message=error_message,
            exempt_when=exempt_when,
            override_defaults=override_defaults,
            deduct_when=deduct_when,
            on_breach=on_breach,
            cost=cost,
        )
        f._limit = _limit
        return f

    return wraps
