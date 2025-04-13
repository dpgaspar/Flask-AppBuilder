from __future__ import annotations

import functools
import json
import logging
import re
import traceback
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TYPE_CHECKING,
    Union,
)
import urllib.parse

from apispec import APISpec, yaml_utils
from apispec.exceptions import DuplicateComponentNameError
from flask import Blueprint, current_app, jsonify, make_response, request, Response
from flask_appbuilder._compat import as_unicode
from flask_appbuilder.api.convert import Model2SchemaConverter
from flask_appbuilder.api.schemas import (
    get_info_schema,
    get_item_schema,
    get_list_schema,
)
from flask_appbuilder.baseviews import AbstractViewApi
from flask_appbuilder.const import (
    API_ADD_COLUMNS_RES_KEY,
    API_ADD_COLUMNS_RIS_KEY,
    API_ADD_TITLE_RES_KEY,
    API_ADD_TITLE_RIS_KEY,
    API_DESCRIPTION_COLUMNS_RES_KEY,
    API_DESCRIPTION_COLUMNS_RIS_KEY,
    API_EDIT_COLUMNS_RES_KEY,
    API_EDIT_COLUMNS_RIS_KEY,
    API_EDIT_TITLE_RES_KEY,
    API_EDIT_TITLE_RIS_KEY,
    API_FILTERS_RES_KEY,
    API_FILTERS_RIS_KEY,
    API_LABEL_COLUMNS_RES_KEY,
    API_LABEL_COLUMNS_RIS_KEY,
    API_LIST_COLUMNS_RES_KEY,
    API_LIST_COLUMNS_RIS_KEY,
    API_LIST_TITLE_RES_KEY,
    API_LIST_TITLE_RIS_KEY,
    API_ORDER_COLUMN_RIS_KEY,
    API_ORDER_COLUMNS_RES_KEY,
    API_ORDER_COLUMNS_RIS_KEY,
    API_ORDER_DIRECTION_RIS_KEY,
    API_PAGE_INDEX_RIS_KEY,
    API_PAGE_SIZE_RIS_KEY,
    API_PERMISSIONS_RES_KEY,
    API_PERMISSIONS_RIS_KEY,
    API_RESULT_RES_KEY,
    API_SELECT_COLUMNS_RIS_KEY,
    API_SELECT_SEL_COLUMNS_RIS_KEY,
    API_SHOW_COLUMNS_RES_KEY,
    API_SHOW_COLUMNS_RIS_KEY,
    API_SHOW_TITLE_RES_KEY,
    API_SHOW_TITLE_RIS_KEY,
    API_URI_RIS_KEY,
    PERMISSION_PREFIX,
)
from flask_appbuilder.exceptions import (
    DatabaseException,
    FABException,
    InvalidOrderByColumnFABException,
)
from flask_appbuilder.hooks import (
    get_before_request_hooks,
    wrap_route_handler_with_hooks,
)
from flask_appbuilder.models.filters import Filters
from flask_appbuilder.models.sqla import Model
from flask_appbuilder.models.sqla.filters import BaseFilter
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import permission_name, protect
from flask_appbuilder.utils.limit import Limit
from flask_babel import lazy_gettext as _
import jsonschema
from marshmallow import Schema, ValidationError
from marshmallow.fields import Field
from marshmallow_sqlalchemy.fields import Related, RelatedList
import prison
from werkzeug.exceptions import BadRequest
import yaml


if TYPE_CHECKING:
    from flask_appbuilder import AppBuilder


log = logging.getLogger(__name__)


ModelKeyType = Union[str, int]
QueryRelatedFieldsFilters = Dict[str, List[List[Any]]]


def get_error_msg() -> str:
    """
    (inspired on Superset code)
    :return: (str)
    """
    if current_app.config.get("FAB_API_SHOW_STACKTRACE"):
        return traceback.format_exc()
    return "Fatal error"


def safe(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator that catches uncaught exceptions and
    return the response in JSON format (inspired on Superset code)
    """

    def wraps(self: "BaseApi", *args: Any, **kwargs: Any) -> Response:
        try:
            return f(self, *args, **kwargs)
        except BadRequest as e:
            return self.response_400(message=str(e))
        except Exception as e:
            log.exception(e)
            return self.response_500(message=get_error_msg())

    return functools.update_wrapper(wraps, f)


def rison(
    schema: Optional[Dict[str, Any]] = None
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Use this decorator to parse URI *Rison* arguments to
    a python data structure, your method gets the data
    structure on kwargs['rison']. Response is HTTP 400
    if *Rison* is not correct::

        class ExampleApi(BaseApi):
                @expose('/risonjson')
                @rison()
                def rison_json(self, **kwargs):
                    return self.response(200, result=kwargs['rison'])

    You can additionally pass a JSON schema to
    validate Rison arguments::

        schema = {
            "type": "object",
            "properties": {
                "arg1": {
                    "type": "integer"
                }
            }
        }

        class ExampleApi(BaseApi):
                @expose('/risonjson')
                @rison(schema)
                def rison_json(self, **kwargs):
                    return self.response(200, result=kwargs['rison'])

    """

    def _rison(f: Callable[..., Any]) -> Callable[..., Any]:
        def wraps(self: "BaseApi", *args: Any, **kwargs: Any) -> Response:
            value = request.args.get(API_URI_RIS_KEY, None)
            kwargs["rison"] = {}
            if value:
                try:
                    kwargs["rison"] = prison.loads(value)
                except prison.decoder.ParserException:
                    if current_app.config.get("FAB_API_ALLOW_JSON_QS", True):
                        # Rison failed try json encoded content
                        try:
                            kwargs["rison"] = json.loads(
                                urllib.parse.parse_qs(f"{API_URI_RIS_KEY}={value}").get(
                                    API_URI_RIS_KEY
                                )[0]
                            )
                        except Exception:
                            return self.response_400(
                                message="Not a valid rison/json argument"
                            )
                    else:
                        return self.response_400(message="Not a valid rison argument")
            if schema:
                try:
                    jsonschema.validate(instance=kwargs["rison"], schema=schema)
                except jsonschema.ValidationError as e:
                    try:
                        validation_message = str(e).split("\n", 1)[0]
                    except Exception:
                        validation_message = str(e)
                    return self.response_400(
                        message=f"Not a valid rison schema {validation_message}"
                    )
            return f(self, *args, **kwargs)

        return functools.update_wrapper(wraps, f)

    return _rison


def expose(url: str = "/", methods: Tuple[str] = ("GET",)) -> Callable[..., Any]:
    """
    Use this decorator to expose API endpoints on your API classes.

    :param url:
        Relative URL for the endpoint
    :param methods:
        Allowed HTTP methods. By default only GET is allowed.
    """

    def wrap(f: Callable[..., Any]) -> Callable[..., Any]:
        if not hasattr(f, "_urls"):
            f._urls = []  # type: ignore
        f._urls.append((url, methods))  # type: ignore
        return f

    return wrap


def merge_response_func(func: Callable[..., Any], key: str) -> Callable[..., Any]:
    """
        Use this decorator to set a new merging
        response function to HTTP endpoints

        candidate function must have the following signature
        and be childs of BaseApi:
        ```
            def merge_some_function(self, response, rison_args):
        ```

    :param func: Name of the merge function where the key is allowed
    :param key: The key name for rison selection
    :return: None
    """

    def wrap(f: Callable[..., Any]) -> Callable[..., Any]:
        if not hasattr(f, "_response_key_func_mappings"):
            f._response_key_func_mappings = {}  # type: ignore
        f._response_key_func_mappings[key] = func  # type: ignore
        return f

    return wrap


class BaseApi(AbstractViewApi):
    """
    All apis inherit from this class.
    it's constructor will register your exposed urls on flask
    as a Blueprint.

    This class does not expose any urls,
    but provides a common base for all APIS.
    """

    endpoint: Optional[str] = None

    version: Optional[str] = "v1"
    """
    Define the Api version for this resource/class
    """
    route_base: Optional[str] = None
    """
    Define the route base where all methods will suffix from
    """
    resource_name: Optional[str] = None
    """
    Defines a custom resource name, overrides the inferred from Class name
    makes no sense to use it with route base
    """
    base_permissions: Optional[List[str]] = None
    """
    A list of allowed base permissions::

        class ExampleApi(BaseApi):
            base_permissions = ['can_get']

    """
    class_permission_name: Optional[str] = None
    """
    Override class permission name default fallback to self.__class__.__name__
    """
    previous_class_permission_name: Optional[str] = None
    """
    If set security converge will replace all permissions tuples
    with this name by the class_permission_name or self.__class__.__name__
    """
    method_permission_name: Optional[Dict[str, str]] = None
    """
    Override method permission names, example::

        method_permissions_name = {
            'get_list': 'read',
            'get': 'read',
            'put': 'write',
            'post': 'write',
            'delete': 'write'
        }
    """
    previous_method_permission_name: Optional[Dict[str, str]] = None
    """
    Use same structure as method_permission_name. If set security converge
    will replace all method permissions by the new ones
    """
    allow_browser_login = False
    """
    Will allow flask-login cookie authorization on the API
    default is False.
    """
    csrf_exempt = True
    """
    If using flask-wtf CSRFProtect exempt the API from check
    """
    apispec_parameter_schemas: Optional[Dict[str, Dict[str, Any]]] = None
    """
    Set your custom Rison parameter schemas here so that
    they get registered on the OpenApi spec::

        custom_parameter = {
            "type": "object"
            "properties": {
                "name": {
                    "type": "string"
                }
            }
        }

        class CustomApi(BaseApi):
            apispec_parameter_schemas = {
                "custom_parameter": custom_parameter
            }
    """
    _apispec_parameter_schemas: Optional[Dict[str, Dict[str, Any]]] = None

    openapi_spec_component_schemas: Tuple[Type[Schema], ...] = tuple()
    """
    A Tuple containing marshmallow schemas to be registered on the OpenAPI spec
    has component schemas, these can be referenced by the endpoint's spec like:
    `$ref: '#/components/schemas/MyCustomSchema'` Where MyCustomSchema is the
    marshmallow schema class name.

    To set your own OpenAPI schema component name, declare your schemas with:
    __component_name__

    class Schema1(Schema):
        __component_name__ = "MyCustomSchema"
        id = fields.Integer()
        ...

    """
    responses = {
        "400": {
            "description": "Bad request",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                    }
                }
            },
        },
        "401": {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                    }
                }
            },
        },
        "403": {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                    }
                }
            },
        },
        "404": {
            "description": "Not found",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                    }
                }
            },
        },
        "422": {
            "description": "Could not process entity",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                    }
                }
            },
        },
        "500": {
            "description": "Fatal error",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                    }
                }
            },
        },
    }
    """
    Override custom OpenApi responses
    """

    exclude_route_methods: Set[str] = set()
    """
    Does not register routes for a set of builtin ModelRestApi functions.
    example::

        class ContactModelView(ModelRestApi):
            datamodel = SQLAInterface(Contact)
            exclude_route_methods = {"info", "get_list", "get"}


    The previous examples will only register the `put`, `post` and `delete` routes
    """
    include_route_methods: Optional[Set[str]] = None
    """
    If defined will assume a white list setup, where all endpoints are excluded
    except those define on this attribute
    example::

        class ContactModelView(ModelRestApi):
            datamodel = SQLAInterface(Contact)
            include_route_methods = {"list"}


    The previous example will exclude all endpoints except the `list` endpoint
    """
    openapi_spec_methods: Dict[str, Any] = {}
    """
    Merge OpenAPI spec defined on the method's doc.
    For example to merge/override `get_list`::


        class GreetingApi(BaseApi):
            resource_name = "greeting"
            openapi_spec_methods = {
                "greeting": {
                    "get": {
                       "description": "Override description",
                    }
                }
            }
    """
    openapi_spec_tag: Optional[str] = None
    """
    By default all endpoints will be tagged (grouped) to their class name.
    Use this attribute to override the tag name
    """

    limits: Optional[List[Limit]] = None
    """
    List of limits for this api.

    Use it like this if you want to restrict the rate of requests to a view::

        class MyView(ModelView):
            limits = [Limit("2 per 5 second")]

    or use the decorator @limit.
    """

    def __init__(self) -> None:
        """
        Initialization of base permissions
        based on exposed methods and actions

        Initialization of extra args
        """
        self.appbuilder = None
        self.blueprint = None

        # Init OpenAPI
        self._response_key_func_mappings: Dict[str, Any] = {}
        self.apispec_parameter_schemas = self.apispec_parameter_schemas or {}
        self._apispec_parameter_schemas = self._apispec_parameter_schemas or {}
        self._apispec_parameter_schemas.update(self.apispec_parameter_schemas)
        if self.openapi_spec_component_schemas is None:
            self.openapi_spec_component_schemas = ()

        # Init class permission override attrs
        if not self.previous_class_permission_name and self.class_permission_name:
            self.previous_class_permission_name = self.__class__.__name__
        self.class_permission_name = (
            self.class_permission_name or self.__class__.__name__
        )

        # Init previous permission override attrs
        is_collect_previous = False
        if not self.previous_method_permission_name and self.method_permission_name:
            self.previous_method_permission_name = dict()
            is_collect_previous = True
        self.method_permission_name = self.method_permission_name or dict()

        # Collect base_permissions and infer previous permissions
        is_add_base_permissions = False
        if self.base_permissions is None:
            self.base_permissions = set()
            is_add_base_permissions = True

        if self.limits is None:
            self.limits = []

        for attr_name in dir(self):
            if hasattr(getattr(self, attr_name), "_limit"):
                self.limits.append(getattr(getattr(self, attr_name), "_limit"))
            # If include_route_methods is not None white list
            if (
                self.include_route_methods is not None
                and attr_name not in self.include_route_methods
            ):
                continue
            # Don't create permission for excluded routes
            if attr_name in self.exclude_route_methods:
                continue
            if hasattr(getattr(self, attr_name), "_permission_name"):
                if is_collect_previous:
                    self.previous_method_permission_name[attr_name] = getattr(
                        getattr(self, attr_name), "_permission_name"
                    )
                _permission_name = self.get_method_permission(attr_name)
                if is_add_base_permissions:
                    self.base_permissions.add(PERMISSION_PREFIX + _permission_name)
        self.base_permissions = list(self.base_permissions)

    def create_blueprint(
        self,
        appbuilder: "AppBuilder",
        endpoint: Optional[str] = None,
        static_folder: Optional[str] = None,
    ) -> Blueprint:
        # Store appbuilder instance
        self.appbuilder = appbuilder
        # If endpoint name is not provided, get it from the class name
        self.endpoint = endpoint or self.__class__.__name__
        self.resource_name = self.resource_name or self.__class__.__name__.lower()

        if self.route_base is None:
            self.route_base = f"/api/{self.version}/{self.resource_name.lower()}"
        self.blueprint = Blueprint(self.endpoint, __name__, url_prefix=self.route_base)
        # Exempt API from CSRF protect
        if self.csrf_exempt:
            csrf = current_app.extensions.get("csrf")
            if csrf:
                csrf.exempt(self.blueprint)

        self._register_urls()
        return self.blueprint

    def add_api_spec(self, api_spec: APISpec) -> None:
        self.add_apispec_components(api_spec)
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, "_urls"):
                for url, methods in attr._urls:
                    # If include_route_methods is not None white list
                    if (
                        self.include_route_methods is not None
                        and attr_name not in self.include_route_methods
                    ):
                        continue
                    if attr_name in self.exclude_route_methods:
                        log.info("Not registering api spec for method %s", attr_name)
                        continue
                    operations = {}
                    path = self.path_helper(path=url, operations=operations)
                    self.operation_helper(
                        path=path, operations=operations, methods=methods, func=attr
                    )
                    api_spec.path(path=path, operations=operations)
                    for operation in operations:
                        openapi_spec_tag = (
                            self.openapi_spec_tag or self.__class__.__name__
                        )
                        api_spec._paths[path][operation]["tags"] = [openapi_spec_tag]

    def add_apispec_components(self, api_spec: APISpec) -> None:
        for k, v in self.responses.items():
            try:
                api_spec.components.response(k, v)
            except DuplicateComponentNameError:
                pass
        for k, v in self._apispec_parameter_schemas.items():
            try:
                api_spec.components.schema(k, v)
            except DuplicateComponentNameError:
                pass
        for schema in self.openapi_spec_component_schemas:
            try:
                if hasattr(schema, "__component_name__"):
                    component_name = schema.__component_name__
                elif isinstance(schema, type):
                    component_name = schema.__name__
                else:
                    component_name = schema.__class__.__name__
                api_spec.components.schema(component_name, schema=schema)
            except DuplicateComponentNameError:
                pass

    def _register_urls(self) -> None:
        before_request_hooks = get_before_request_hooks(self)
        for attr_name in dir(self):
            if (
                self.include_route_methods is not None
                and attr_name not in self.include_route_methods
            ):
                continue
            if attr_name in self.exclude_route_methods:
                log.debug("Not registering route for method %s", attr_name)
                continue
            attr = getattr(self, attr_name)
            if hasattr(attr, "_urls"):
                for url, methods in attr._urls:
                    log.debug(
                        "Registering route %s%s %s",
                        self.blueprint.url_prefix,
                        url,
                        methods,
                    )
                    route_handler = wrap_route_handler_with_hooks(
                        attr_name, attr, before_request_hooks
                    )
                    self.blueprint.add_url_rule(
                        url, attr_name, route_handler, methods=methods
                    )

    def path_helper(
        self,
        path: str = None,
        operations: Optional[Dict[str, Dict]] = None,
        **kwargs: Any,
    ) -> str:
        """
            Works like an apispec plugin
            May return a path as string and mutate operations dict.

        :param str path: Path to the resource
        :param dict operations: A `dict` mapping HTTP methods to operation object. See
            https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#operationObject
        :param kwargs:
        :return: Return value should be a string or None. If a string is returned, it
        is set as the path.
        """
        RE_URL = re.compile(r"<(?:[^:<>]+:)?([^<>]+)>")
        path = RE_URL.sub(r"{\1}", path)
        return f"{self.route_base}{path}"

    def operation_helper(
        self,
        path: Optional[str] = None,
        operations: Dict[str, Any] = None,
        methods: List[str] = None,
        func: Callable[..., Response] = None,
        **kwargs: Any,
    ) -> None:
        """May mutate operations.
        :param str path: Path to the resource
        :param dict operations: A `dict` mapping HTTP methods to operation object.
        :param list methods: A list of HTTP methods registered for this path
        """
        for method in methods:
            try:
                # Check if method openapi spec is overridden
                override_method_spec = self.openapi_spec_methods[func.__name__]
            except KeyError:
                override_method_spec = {}
            yaml_doc_string = yaml_utils.load_operations_from_docstring(func.__doc__)
            yaml_doc_string = yaml.safe_load(
                str(yaml_doc_string).replace(
                    "{{self.__class__.__name__}}", self.__class__.__name__
                )
            )
            if yaml_doc_string:
                operation_spec = yaml_doc_string.get(method.lower(), {})
                # Merge docs spec and override spec
                operation_spec.update(override_method_spec.get(method.lower(), {}))
                if self.get_method_permission(func.__name__):
                    operation_spec["security"] = [{"jwt": []}]
                operations[method.lower()] = operation_spec
            else:
                operations[method.lower()] = {}

    @staticmethod
    def _prettify_name(name: str) -> str:
        """
        Prettify pythonic variable name.

        For example, 'HelloWorld' will be converted to 'Hello World'

        :param name:
            Name to prettify.
        """
        return re.sub(r"(?<=.)([A-Z])", r" \1", name)

    @staticmethod
    def _prettify_column(name: str) -> str:
        """
        Prettify pythonic variable name.

        For example, 'hello_world' will be converted to 'Hello World'

        :param name:
            Name to prettify.
        """
        return re.sub("[._]", " ", name).title()

    def get_uninit_inner_views(self) -> List[Type[AbstractViewApi]]:
        """
        Will return a list with views that need to be initialized.
        Normally related_views from ModelView
        """
        return []

    def get_init_inner_views(self) -> List[AbstractViewApi]:
        """
        Sets initialized inner views
        """
        pass  # pragma: no cover

    def get_method_permission(self, method_name: str) -> str:
        """
        Returns the permission name for a method
        """
        if self.method_permission_name:
            return self.method_permission_name.get(method_name, method_name)
        else:
            if hasattr(getattr(self, method_name), "_permission_name"):
                return getattr(getattr(self, method_name), "_permission_name")

    def set_response_key_mappings(
        self,
        response: Dict[str, Any],
        func: Callable[..., Response],
        rison_args: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        if not hasattr(func, "_response_key_func_mappings"):
            return  # pragma: no cover
        _keys = rison_args.get("keys", None)
        if not _keys:
            for k, v in func._response_key_func_mappings.items():
                v(self, response, **kwargs)
        else:
            for k, v in func._response_key_func_mappings.items():
                if k in _keys:
                    v(self, response, **kwargs)

    def merge_current_user_permissions(
        self, response: Dict[str, Any], **kwargs: Any
    ) -> None:
        response[API_PERMISSIONS_RES_KEY] = [
            permission
            for permission in self.base_permissions
            if self.appbuilder.sm.has_access(permission, self.class_permission_name)
        ]

    @staticmethod
    def response(code: int, **kwargs: Any) -> Response:
        """
        Generic HTTP JSON response method

        :param code: HTTP code (int)
        :param kwargs: Data structure for response (dict)
        :return: HTTP Json response
        """
        _ret_json = jsonify(kwargs)
        resp = make_response(_ret_json, code)
        resp.headers["Content-Type"] = "application/json; charset=utf-8"
        return resp

    def response_400(self, message: str = None) -> Response:
        """
        Helper method for HTTP 400 response

        :param message: Error message (str)
        :return: HTTP Json response
        """
        message = message or "Arguments are not correct"
        return self.response(400, **{"message": message})

    def response_422(self, message: str = None) -> Response:
        """
        Helper method for HTTP 422 response

        :param message: Error message (str)
        :return: HTTP Json response
        """
        message = message or "Could not process entity"
        return self.response(422, **{"message": message})

    def response_401(self) -> Response:
        """
        Helper method for HTTP 401 response

        :param message: Error message (str)
        :return: HTTP Json response
        """
        return self.response(401, **{"message": "Not authorized"})

    def response_403(self) -> Response:
        """
        Helper method for HTTP 403 response

        :param message: Error message (str)
        :return: HTTP Json response
        """
        return self.response(403, **{"message": "Forbidden"})

    def response_404(self) -> Response:
        """
        Helper method for HTTP 404 response

        :param message: Error message (str)
        :return: HTTP Json response
        """
        return self.response(404, **{"message": "Not found"})

    def response_500(self, message: str = None) -> Response:
        """
        Helper method for HTTP 500 response

        :param message: Error message (str)
        :return: HTTP Json response
        """
        message = message or "Internal error"
        return self.response(500, **{"message": message})


class ModelRestApi(BaseApi):
    datamodel: SQLAInterface
    """
    Your sqla model you must initialize it like::

        class MyModelApi(BaseModelApi):
            datamodel = SQLAInterface(MyTable)
    """
    search_columns = None
    """
    List with allowed search columns, if not provided all possible search
    columns will be used. If you want to limit the search (*filter*) columns
     possibilities, define it with a list of column names from your model::

        class MyView(ModelRestApi):
            datamodel = SQLAInterface(MyTable)
            search_columns = ['name', 'address']

    """
    search_filters: dict[str, BaseFilter] | None = None
    """
    Override default search filters for columns
    """
    search_exclude_columns = None
    """
    List with columns to exclude from search. Search includes all possible
    columns by default
    """
    label_columns = None
    """
    Dictionary of labels for your columns, override this if you want
     different pretify labels

    example (will just override the label for name column)::

        class MyView(ModelRestApi):
            datamodel = SQLAInterface(MyTable)
            label_columns = {'name':'My Name Label Override'}

    """
    base_filters = None
    """
    Filter the view use: [['column_name',BaseFilter,'value'],]

    example::

        def get_user():
            return g.user

        class MyView(ModelRestApi):
            datamodel = SQLAInterface(MyTable)
            base_filters = [['created_by', FilterEqualFunction, get_user],
                            ['name', FilterStartsWith, 'a']]

    """

    base_order = None
    """
    Use this property to set default ordering for lists
     ('col_name','asc|desc')::

        class MyView(ModelRestApi):
            datamodel = SQLAInterface(MyTable)
            base_order = ('my_column_name','asc')

    """
    _base_filters = None
    """ Internal base Filter from class Filters will always filter view """
    _filters = None
    """
    Filters object will calculate all possible filter types
    based on search_columns
    """
    list_title = ""
    """
    List Title, if not configured the default is
    'List ' with pretty model name
    """
    show_title: Optional[str] = ""
    """
    Show Title , if not configured the default is
    'Show ' with pretty model name
    """
    add_title: Optional[str] = ""
    """
    Add Title , if not configured the default is
    'Add ' with pretty model name
    """
    edit_title: Optional[str] = ""
    """
    Edit Title , if not configured the default is
    'Edit ' with pretty model name
    """
    list_select_columns: Optional[List[str]] = None
    """
    A List of column names that will be included on the SQL select.
    This is useful for including all necessary columns that are referenced
    by properties listed on `list_columns` without generating N+1 queries.
    """
    list_outer_default_load = False
    """
    If True, the default load for outer joins will be applied on the get item endpoint.
    This is useful for when you want to control the load of the many-to-many and
    many-to-one relationships at the model level. Will apply:
     https://docs.sqlalchemy.org/en/14/orm/loading_relationships.html#sqlalchemy.orm.Load.defaultload
    """
    list_columns: Optional[List[str]] = None
    """
    A list of columns (or model's methods) to be displayed on the list view.
    Use it to control the order of the display
    """
    show_select_columns: Optional[List[str]] = None
    """
    A List of column names that will be included on the SQL select.
    This is useful for including all necessary columns that are referenced
    by properties listed on `show_columns` without generating N+1 queries.
    """
    show_outer_default_load = False
    """
    If True, the default load for outer joins will be applied on the get item endpoint.
    This is useful for when you want to control the load of the many-to-many and
    many-to-one relationships at the model level. Will apply:
     https://docs.sqlalchemy.org/en/14/orm/loading_relationships.html#sqlalchemy.orm.Load.defaultload
    """
    show_columns: Optional[List[str]] = None
    """
    A list of columns (or model's methods) for the get item endpoint.
    Use it to control the order of the results
    """
    add_columns: Optional[List[str]] = None
    """
    A list of columns (or model's methods) to be allowed to post
    """
    edit_columns: Optional[List[str]] = None
    """
    A list of columns (or model's methods) to be allowed to update
    """
    list_exclude_columns: Optional[List[str]] = None
    """
    A list of columns to exclude from the get list endpoint.
    By default all columns are included.
    """
    show_exclude_columns: Optional[List[str]] = None
    """
    A list of columns to exclude from the get item endpoint.
    By default all columns are included.
    """
    add_exclude_columns: Optional[List[str]] = None
    """
    A list of columns to exclude from the add endpoint.
    By default all columns are included.
    """
    edit_exclude_columns: Optional[List[str]] = None
    """
    A list of columns to exclude from the edit endpoint.
    By default all columns are included.
    """
    order_columns: Optional[List[str]] = None
    """ Allowed order columns """
    page_size = 20
    """
    Use this property to change default page size
    """
    max_page_size: Optional[int] = None
    """
    class override for the FAB_API_MAX_SIZE, use special -1 to allow for any page
    size
    """
    description_columns: Optional[Dict[str, str]] = None
    """
    Dictionary with column descriptions that will be shown on the forms::

        class MyView(ModelRestApi):
            datamodel = SQLAModel(Model1)
            description_columns = {'name':'your models name column',
                                    'address':'the address column'}
    """
    validators_columns: Optional[Dict[str, Callable]] = None
    """ Dictionary to add your own marshmallow validators """

    add_query_rel_fields = None
    """
    Add Customized query for related add fields.
    Assign a dictionary where the keys are the column names of
    the related models to filter, the value for each key, is a list of lists with the
    same format as base_filter
    {'relation col name':[['Related model col',FilterClass,'Filter Value'],...],...}
    Add a custom filter to form related fields::

        class ContactModelView(ModelRestApi):
            datamodel = SQLAModel(Contact)
            add_query_rel_fields = {'group':[['name',FilterStartsWith,'W']]}

    """
    edit_query_rel_fields = None
    """
    Add Customized query for related edit fields.
    Assign a dictionary where the keys are the column names of
    the related models to filter, the value for each key, is a list of lists with the
    same format as base_filter
    {'relation col name':[['Related model col',FilterClass,'Filter Value'],...],...}
    Add a custom filter to form related fields::

        class ContactModelView(ModelRestApi):
            datamodel = SQLAModel(Contact)
            edit_query_rel_fields = {'group':[['name',FilterStartsWith,'W']]}

    """
    order_rel_fields = None
    """
    Impose order on related fields.
    assign a dictionary where the keys are the related column names::

        class ContactModelView(ModelRestApi):
            datamodel = SQLAModel(Contact)
            order_rel_fields = {
                'group': ('name', 'asc')
                'gender': ('name', 'asc')
            }
    """
    list_model_schema: Optional[Schema] = None
    """
    Override to provide your own marshmallow Schema
    for JSON to SQLA dumps
    """
    add_model_schema: Optional[Schema] = None
    """
    Override to provide your own marshmallow Schema
    for JSON to SQLA dumps
    """
    edit_model_schema: Optional[Schema] = None
    """
    Override to provide your own marshmallow Schema
    for JSON to SQLA dumps
    """
    show_model_schema: Optional[Schema] = None
    """
    Override to provide your own marshmallow Schema
    for JSON to SQLA dumps
    """
    model2schemaconverter = Model2SchemaConverter
    """
    Override to use your own Model2SchemaConverter
    (inherit from BaseModel2SchemaConverter)
    """
    _apispec_parameter_schemas = {
        "get_info_schema": get_info_schema,
        "get_item_schema": get_item_schema,
        "get_list_schema": get_list_schema,
    }

    def __init__(self) -> None:
        super().__init__()
        self._init_properties()
        self._init_titles()
        self.validators_columns = self.validators_columns or {}
        self.model2schemaconverter = self.model2schemaconverter(
            self.datamodel, self.validators_columns
        )

    def create_blueprint(
        self, appbuilder: "AppBuilder", *args: Any, **kwargs: Any
    ) -> Blueprint:
        self._init_model_schemas()
        return super().create_blueprint(appbuilder, *args, **kwargs)

    @property
    def list_model_schema_name(self) -> str:
        return f"{self.__class__.__name__}.get_list"

    @property
    def show_model_schema_name(self) -> str:
        return f"{self.__class__.__name__}.get"

    @property
    def add_model_schema_name(self) -> str:
        return f"{self.__class__.__name__}.post"

    @property
    def edit_model_schema_name(self) -> str:
        return f"{self.__class__.__name__}.put"

    def add_apispec_components(self, api_spec: APISpec) -> None:
        super().add_apispec_components(api_spec)
        api_spec.components.schema(
            self.list_model_schema_name, schema=self.list_model_schema
        )
        api_spec.components.schema(
            self.add_model_schema_name, schema=self.add_model_schema
        )
        api_spec.components.schema(
            self.edit_model_schema_name, schema=self.edit_model_schema
        )
        api_spec.components.schema(
            self.show_model_schema_name, schema=self.show_model_schema
        )

    def _gen_labels_columns(self, list_columns: List[str]) -> None:
        """
        Auto generates pretty label_columns from list of columns
        """
        for col in list_columns:
            if not self.label_columns.get(col):
                self.label_columns[col] = self._prettify_column(col)

    def _label_columns_json(self, cols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Prepares dict with labels to be JSON serializable
        """
        ret = {}
        cols = cols or []
        d = {k: v for (k, v) in self.label_columns.items() if k in cols}
        for key, value in d.items():
            ret[key] = as_unicode(_(value).encode("UTF-8"))
        return ret

    def _init_model_schemas(self) -> None:
        # Create Marshmalow schemas if one is not specified
        if self.list_model_schema is None:
            self.list_model_schema = self.model2schemaconverter.convert(
                self.list_columns, parent_schema_name=self.list_model_schema_name
            )
        if self.add_model_schema is None:
            self.add_model_schema = self.model2schemaconverter.convert(
                self.add_columns,
                nested=False,
                parent_schema_name=self.add_model_schema_name,
            )
        if self.edit_model_schema is None:
            self.edit_model_schema = self.model2schemaconverter.convert(
                self.edit_columns,
                nested=False,
                parent_schema_name=self.edit_model_schema_name,
            )
        if self.show_model_schema is None:
            self.show_model_schema = self.model2schemaconverter.convert(
                self.show_columns, parent_schema_name=self.show_model_schema_name
            )

    def _init_titles(self) -> None:
        """
        Init Titles if not defined
        """
        class_name = self.datamodel.model_name
        if not self.list_title:
            self.list_title = "List " + self._prettify_name(class_name)
        if not self.add_title:
            self.add_title = "Add " + self._prettify_name(class_name)
        if not self.edit_title:
            self.edit_title = "Edit " + self._prettify_name(class_name)
        if not self.show_title:
            self.show_title = "Show " + self._prettify_name(class_name)
        self.title = self.list_title

    def _init_properties(self) -> None:
        """
        Initializes all properties
        """
        self.label_columns = self.label_columns or {}
        self.base_filters = self.base_filters or []
        self.search_exclude_columns = self.search_exclude_columns or []
        self.search_columns = self.search_columns or []

        self._base_filters = self.datamodel.get_filters().add_filter_list(
            self.base_filters
        )
        search_columns = self.datamodel.get_search_columns_list()
        if not self.search_columns:
            self.search_columns = [
                x for x in search_columns if x not in self.search_exclude_columns
            ]
        self._gen_labels_columns(self.datamodel.get_columns_list())

        # Reset init props
        self.description_columns = self.description_columns or {}
        self.list_exclude_columns = self.list_exclude_columns or []
        self.show_exclude_columns = self.show_exclude_columns or []
        self.add_exclude_columns = self.add_exclude_columns or []
        self.edit_exclude_columns = self.edit_exclude_columns or []
        self.order_rel_fields = self.order_rel_fields or {}
        # Generate base props
        list_cols = self.datamodel.get_user_columns_list()
        if not self.list_columns and self.list_model_schema:
            list(self.list_model_schema._declared_fields.keys())
        else:
            self.list_columns = self.list_columns or [
                x
                for x in self.datamodel.get_user_columns_list()
                if x not in self.list_exclude_columns
            ]
        self.list_select_columns = self.list_select_columns or self.list_columns

        self.order_columns = (
            self.order_columns
            or self.datamodel.get_order_columns_list(list_columns=self.list_columns)
        )
        # Process excluded columns
        if not self.show_columns:
            self.show_columns = [
                x for x in list_cols if x not in self.show_exclude_columns
            ]
        self.show_select_columns = self.show_select_columns or self.show_columns

        if not self.add_columns:
            self.add_columns = [
                x for x in list_cols if x not in self.add_exclude_columns
            ]
        if not self.edit_columns:
            self.edit_columns = [
                x for x in list_cols if x not in self.edit_exclude_columns
            ]
        self._gen_labels_columns(self.list_columns)
        self._gen_labels_columns(self.show_columns)
        self._filters = self.datamodel.get_filters(
            search_columns=self.search_columns, search_filters=self.search_filters
        )
        self.edit_query_rel_fields = self.edit_query_rel_fields or dict()
        self.add_query_rel_fields = self.add_query_rel_fields or dict()

    def merge_add_field_info(self, response: Dict[str, Any], **kwargs: Any) -> None:
        add_columns_info = kwargs.get("add_columns", {})
        response[API_ADD_COLUMNS_RES_KEY] = self._get_fields_info(
            self.add_columns,
            self.add_model_schema,
            self.add_query_rel_fields,
            **add_columns_info,
        )

    def merge_edit_field_info(self, response: Dict[str, Any], **kwargs: Any) -> None:
        edit_columns_info = kwargs.get("edit_columns", {})
        response[API_EDIT_COLUMNS_RES_KEY] = self._get_fields_info(
            self.edit_columns,
            self.edit_model_schema,
            self.edit_query_rel_fields,
            **edit_columns_info,
        )

    def merge_search_filters(self, response: Dict[str, Any], **kwargs: Any) -> None:
        # Get possible search fields and all possible operations
        search_filters = {}
        dict_filters = self._filters.get_search_filters()
        for col in self.search_columns:
            if col not in dict_filters:
                # column not in search filters but defined has one
                continue
            search_filters[col] = [
                {"name": as_unicode(flt.name), "operator": flt.arg_name}
                for flt in dict_filters[col]
            ]
        response[API_FILTERS_RES_KEY] = search_filters

    def merge_add_title(self, response: Dict[str, Any], **kwargs: Any) -> None:
        response[API_ADD_TITLE_RES_KEY] = self.add_title

    def merge_edit_title(self, response: Dict[str, Any], **kwargs: Any) -> None:
        response[API_EDIT_TITLE_RES_KEY] = self.edit_title

    def merge_label_columns(self, response: Dict[str, Any], **kwargs: Any) -> None:
        pruned_select_cols = kwargs.get(API_SELECT_COLUMNS_RIS_KEY, [])
        if pruned_select_cols:
            columns = pruned_select_cols
        else:
            # Send the exact labels for the caller operation
            if kwargs.get("caller") == "list":
                columns = self.list_columns
            elif kwargs.get("caller") == "show":
                columns = self.show_columns
            else:
                columns = self.label_columns  # pragma: no cover
        response[API_LABEL_COLUMNS_RES_KEY] = self._label_columns_json(columns)

    def merge_list_label_columns(self, response: Dict[str, Any], **kwargs: Any) -> None:
        self.merge_label_columns(response, caller="list", **kwargs)

    def merge_show_label_columns(self, response: Dict[str, Any], **kwargs: Any) -> None:
        self.merge_label_columns(response, caller="show", **kwargs)

    def merge_show_columns(self, response: Dict[str, Any], **kwargs: Any) -> None:
        pruned_select_cols = kwargs.get(API_SELECT_COLUMNS_RIS_KEY, [])
        if pruned_select_cols:
            response[API_SHOW_COLUMNS_RES_KEY] = pruned_select_cols
        else:
            response[API_SHOW_COLUMNS_RES_KEY] = self.show_columns

    def merge_description_columns(
        self, response: Dict[str, Any], **kwargs: Any
    ) -> None:
        pruned_select_cols = kwargs.get(API_SELECT_COLUMNS_RIS_KEY, [])
        if pruned_select_cols:
            response[API_DESCRIPTION_COLUMNS_RES_KEY] = self._description_columns_json(
                pruned_select_cols
            )
        else:
            # Send all descriptions if cols are or request pruned
            response[API_DESCRIPTION_COLUMNS_RES_KEY] = self._description_columns_json(
                self.description_columns
            )

    def merge_list_columns(self, response: Dict[str, Any], **kwargs: Any) -> None:
        pruned_select_cols = kwargs.get(API_SELECT_COLUMNS_RIS_KEY, [])
        if pruned_select_cols:
            response[API_LIST_COLUMNS_RES_KEY] = pruned_select_cols
        else:
            response[API_LIST_COLUMNS_RES_KEY] = self.list_columns

    def merge_order_columns(self, response: Dict[str, Any], **kwargs: Any) -> None:
        pruned_select_cols = kwargs.get(API_SELECT_COLUMNS_RIS_KEY, [])
        if pruned_select_cols:
            response[API_ORDER_COLUMNS_RES_KEY] = [
                order_col
                for order_col in self.order_columns
                if order_col in pruned_select_cols
            ]
        else:
            response[API_ORDER_COLUMNS_RES_KEY] = self.order_columns

    def merge_list_title(self, response: Dict[str, Any], **kwargs: Any) -> None:
        response[API_LIST_TITLE_RES_KEY] = self.list_title

    def merge_show_title(self, response: Dict[str, Any], **kwargs: Any) -> None:
        response[API_SHOW_TITLE_RES_KEY] = self.show_title

    def info_headless(self, **kwargs: Any) -> Response:
        """
        response for CRUD REST meta data
        """
        payload = {}
        rison_args = kwargs.get("rison", {})
        self.set_response_key_mappings(payload, self.info, rison_args, **rison_args)
        return self.response(200, **payload)

    @expose("/_info", methods=["GET"])
    @protect()
    @safe
    @rison(get_info_schema)
    @permission_name("info")
    @merge_response_func(
        BaseApi.merge_current_user_permissions, API_PERMISSIONS_RIS_KEY
    )
    @merge_response_func(merge_add_field_info, API_ADD_COLUMNS_RIS_KEY)
    @merge_response_func(merge_edit_field_info, API_EDIT_COLUMNS_RIS_KEY)
    @merge_response_func(merge_search_filters, API_FILTERS_RIS_KEY)
    @merge_response_func(merge_add_title, API_ADD_TITLE_RIS_KEY)
    @merge_response_func(merge_edit_title, API_EDIT_TITLE_RIS_KEY)
    def info(self, **kwargs: Any) -> Response:
        """Endpoint that renders a response for CRUD REST meta data
        ---
        get:
          description: >-
            Get metadata information about this API resource
          parameters:
          - in: query
            name: q
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/get_info_schema'
          responses:
            200:
              description: Item from Model
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      add_columns:
                        type: object
                      edit_columns:
                        type: object
                      filters:
                        type: object
                        properties:
                          column_name:
                            type: array
                            items:
                              type: object
                              properties:
                                name:
                                  description: >-
                                    The filter name. Will be translated by babel
                                  type: string
                                operator:
                                  description: >-
                                    The filter operation key to use on list filters
                                  type: string
                      permissions:
                        description: The user permissions for this API resource
                        type: array
                        items:
                          type: string
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            422:
              $ref: '#/components/responses/422'
            500:
              $ref: '#/components/responses/500'
        """
        return self.info_headless(**kwargs)

    def get_headless(self, pk: ModelKeyType, **kwargs: Any) -> Response:
        """
            Get an item from Model

        :param pk: Item primary key
        :param kwargs: Query string parameter arguments
        :return: HTTP Response
        """
        item = self.datamodel.get(
            pk,
            self._base_filters,
            self.show_select_columns,
            self.show_outer_default_load,
        )
        if not item:
            return self.response_404()

        response = {}
        args = kwargs.get("rison", {})
        select_cols = args.get(API_SELECT_COLUMNS_RIS_KEY, [])
        pruned_select_cols = [col for col in select_cols if col in self.show_columns]
        self.set_response_key_mappings(
            response, self.get, args, **{API_SELECT_COLUMNS_RIS_KEY: pruned_select_cols}
        )
        if pruned_select_cols:
            show_model_schema = self.model2schemaconverter.convert(pruned_select_cols)
        else:
            show_model_schema = self.show_model_schema

        response["id"] = pk
        response[API_RESULT_RES_KEY] = show_model_schema.dump(item, many=False)
        self.pre_get(response)
        return self.response(200, **response)

    @expose("/<int:pk>", methods=["GET"])
    @protect()
    @safe
    @permission_name("get")
    @rison(get_item_schema)
    @merge_response_func(merge_show_label_columns, API_LABEL_COLUMNS_RIS_KEY)
    @merge_response_func(merge_show_columns, API_SHOW_COLUMNS_RIS_KEY)
    @merge_response_func(merge_description_columns, API_DESCRIPTION_COLUMNS_RIS_KEY)
    @merge_response_func(merge_show_title, API_SHOW_TITLE_RIS_KEY)
    def get(self, pk: ModelKeyType, **kwargs: Any) -> Response:
        """Get item from Model
        ---
        get:
          description: >-
            Get an item model
          parameters:
          - in: path
            schema:
              type: integer
            name: pk
          - in: query
            name: q
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/get_item_schema'
          responses:
            200:
              description: Item from Model
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      label_columns:
                        type: object
                        properties:
                          column_name:
                            description: >-
                              The label for the column name.
                              Will be translated by babel
                            example: A Nice label for the column
                            type: string
                      show_columns:
                        description: >-
                          A list of columns
                        type: array
                        items:
                          type: string
                      description_columns:
                        type: object
                        properties:
                          column_name:
                            description: >-
                              The description for the column name.
                              Will be translated by babel
                            example: A Nice description for the column
                            type: string
                      show_title:
                        description: >-
                          A title to render.
                          Will be translated by babel
                        example: Show Item Details
                        type: string
                      id:
                        description: The item id
                        type: string
                      result:
                        $ref: '#/components/schemas/{{self.__class__.__name__}}.get'
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            404:
              $ref: '#/components/responses/404'
            422:
              $ref: '#/components/responses/422'
            500:
              $ref: '#/components/responses/500'
        """
        return self.get_headless(pk, **kwargs)

    def get_list_headless(self, **kwargs: Any) -> Response:
        """
        Get list of items from Model
        """
        response = dict()
        args = kwargs.get("rison", {})
        # handle select columns
        output_select_cols = args.get(API_SELECT_COLUMNS_RIS_KEY, [])
        select_cols = args.get(API_SELECT_SEL_COLUMNS_RIS_KEY, [])
        if select_cols and output_select_cols:
            return self.response_400(message="Cannot use both select and sel columns")
        list_select_columns = self.list_select_columns
        pruned_select_cols = []
        if output_select_cols:
            pruned_select_cols = [
                col for col in output_select_cols if col in self.list_columns
            ]
        if select_cols:
            pruned_select_cols = [
                col for col in select_cols if col in self.list_columns
            ]
            list_select_columns = [
                col for col in select_cols if col in self.list_select_columns
            ]
        # map decorated metadata
        self.set_response_key_mappings(
            response,
            self.get_list,
            args,
            **{API_SELECT_COLUMNS_RIS_KEY: pruned_select_cols},
        )
        # Create a response schema with the computed response columns,
        # defined or requested
        if pruned_select_cols:
            list_model_schema = self.model2schemaconverter.convert(pruned_select_cols)
        else:
            list_model_schema = self.list_model_schema
        # handle filters
        try:
            joined_filters = self._handle_filters_args(args)
        except FABException as e:
            return self.response_400(message=str(e))
        # handle base order
        try:
            order_column, order_direction = self._handle_order_args(args)
        except InvalidOrderByColumnFABException as e:
            return self.response_400(message=str(e))
        # handle pagination
        page_index, page_size = self._handle_page_args(args)
        # Make the query
        count, lst = self.datamodel.query(
            joined_filters,
            order_column,
            order_direction,
            page=page_index,
            page_size=page_size,
            select_columns=list_select_columns,
            outer_default_load=self.list_outer_default_load,
        )
        pks = self.datamodel.get_keys(lst)
        response[API_RESULT_RES_KEY] = list_model_schema.dump(lst, many=True)
        response["ids"] = pks
        response["count"] = count
        self.pre_get_list(response)
        return self.response(200, **response)

    @expose("/", methods=["GET"])
    @protect()
    @safe
    @permission_name("get")
    @rison(get_list_schema)
    @merge_response_func(merge_order_columns, API_ORDER_COLUMNS_RIS_KEY)
    @merge_response_func(merge_list_label_columns, API_LABEL_COLUMNS_RIS_KEY)
    @merge_response_func(merge_description_columns, API_DESCRIPTION_COLUMNS_RIS_KEY)
    @merge_response_func(merge_list_columns, API_LIST_COLUMNS_RIS_KEY)
    @merge_response_func(merge_list_title, API_LIST_TITLE_RIS_KEY)
    def get_list(self, **kwargs: Any) -> Response:
        """Get list of items from Model
        ---
        get:
          description: >-
            Get a list of models
          parameters:
          - in: query
            name: q
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/get_list_schema'
          responses:
            200:
              description: Items from Model
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      label_columns:
                        type: object
                        properties:
                          column_name:
                            description: >-
                              The label for the column name.
                              Will be translated by babel
                            example: A Nice label for the column
                            type: string
                      list_columns:
                        description: >-
                          A list of columns
                        type: array
                        items:
                          type: string
                      description_columns:
                        type: object
                        properties:
                          column_name:
                            description: >-
                              The description for the column name.
                              Will be translated by babel
                            example: A Nice description for the column
                            type: string
                      list_title:
                        description: >-
                          A title to render.
                          Will be translated by babel
                        example: List Items
                        type: string
                      ids:
                        description: >-
                          A list of item ids, useful when you don't know the column id
                        type: array
                        items:
                          type: string
                      count:
                        description: >-
                          The total record count on the backend
                        type: number
                      order_columns:
                        description: >-
                          A list of allowed columns to sort
                        type: array
                        items:
                          type: string
                      result:
                        description: >-
                          The result from the get list query
                        type: array
                        items:
                          $ref: '#/components/schemas/{{self.__class__.__name__}}.get_list'  # noqa
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            422:
              $ref: '#/components/responses/422'
            500:
              $ref: '#/components/responses/500'
        """
        return self.get_list_headless(**kwargs)

    def post_headless(self) -> Response:
        """
        POST/Add item to Model
        """
        if not request.is_json:
            return self.response_400(message="Request is not JSON")
        try:
            item = self.add_model_schema.load(request.json)
        except ValidationError as err:
            return self.response_422(message=err.messages)
        # This validates custom Schema with custom validations
        self.pre_add(item)
        try:
            self.datamodel.add(item)
            self.post_add(item)
            return self.response(
                201,
                **{
                    API_RESULT_RES_KEY: self.add_model_schema.dump(item, many=False),
                    "id": self.datamodel.get_pk_value(item),
                },
            )
        except DatabaseException as e:
            return self.response_422(
                message=f"Database exception occurred: {e.__cause__}"
            )

    @expose("/", methods=["POST"])
    @protect()
    @safe
    @permission_name("post")
    def post(self) -> Response:
        """POST item to Model
        ---
        post:
          requestBody:
            description: Model schema
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/{{self.__class__.__name__}}.post'
          responses:
            201:
              description: Item inserted
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      id:
                        type: string
                      result:
                        $ref: '#/components/schemas/{{self.__class__.__name__}}.post'
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            422:
              $ref: '#/components/responses/422'
            500:
              $ref: '#/components/responses/500'
        """
        return self.post_headless()

    def put_headless(self, pk: ModelKeyType) -> Response:
        """
        PUT/Edit item to Model
        """
        item = self.datamodel.get(pk, self._base_filters)
        if not request.is_json:
            return self.response(400, **{"message": "Request is not JSON"})
        if not item:
            return self.response_404()
        try:
            data = self._merge_update_item(item, request.json)
            item = self.edit_model_schema.load(data, instance=item)
        except ValidationError as err:
            return self.response_422(message=err.messages)
        self.pre_update(item)
        try:
            self.datamodel.edit(item)
            self.post_update(item)
            return self.response(
                200,
                **{API_RESULT_RES_KEY: self.edit_model_schema.dump(item, many=False)},
            )
        except DatabaseException as e:
            return self.response_422(
                message=f"Database exception occurred: {e.__cause__}"
            )

    @expose("/<pk>", methods=["PUT"])
    @protect()
    @safe
    @permission_name("put")
    def put(self, pk: ModelKeyType) -> Response:
        """PUT item to Model
        ---
        put:
          parameters:
          - in: path
            schema:
              type: integer
            name: pk
          requestBody:
            description: Model schema
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/{{self.__class__.__name__}}.put'
          responses:
            200:
              description: Item changed
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      result:
                        $ref: '#/components/schemas/{{self.__class__.__name__}}.put'
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            404:
              $ref: '#/components/responses/404'
            422:
              $ref: '#/components/responses/422'
            500:
              $ref: '#/components/responses/500'
        """
        return self.put_headless(pk)

    def delete_headless(self, pk: ModelKeyType) -> Response:
        """
        Delete item from Model
        """
        item = self.datamodel.get(pk, self._base_filters)
        if not item:
            return self.response_404()
        self.pre_delete(item)
        try:
            self.datamodel.delete(item)
            self.post_delete(item)
            return self.response(200, message="OK")
        except DatabaseException as e:
            return self.response_422(
                message=f"Database exception occurred: {e.__cause__}"
            )

    @expose("/<pk>", methods=["DELETE"])
    @protect()
    @safe
    @permission_name("delete")
    def delete(self, pk: ModelKeyType) -> Response:
        """Delete item from Model
        ---
        delete:
          parameters:
          - in: path
            schema:
              type: integer
            name: pk
          responses:
            200:
              description: Item deleted
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message:
                        type: string
            404:
              $ref: '#/components/responses/404'
            422:
              $ref: '#/components/responses/422'
            500:
              $ref: '#/components/responses/500'
        """
        return self.delete_headless(pk)

    """
    ------------------------------------------------
                HELPER FUNCTIONS
    ------------------------------------------------
    """

    def _handle_page_args(
        self, rison_args: Dict[str, Any]
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Helper function to handle rison page
        arguments, sets defaults and impose
        FAB_API_MAX_PAGE_SIZE

        :param rison_args:
        :return: (tuple) page, page_size
        """
        page = rison_args.get(API_PAGE_INDEX_RIS_KEY, 0)
        page_size = rison_args.get(API_PAGE_SIZE_RIS_KEY, self.page_size)
        return self._sanitize_page_args(page, page_size)

    def _sanitize_page_args(
        self, page: Optional[int], page_size: Optional[int]
    ) -> Tuple[Optional[int], Optional[int]]:
        page_ = page or 0
        page_size_ = page_size or self.page_size
        max_page_size = self.max_page_size or current_app.config.get(
            "FAB_API_MAX_PAGE_SIZE"
        )
        # Accept special -1 to uncap the page size
        if max_page_size == -1:
            if page_size_ == -1:
                return None, None
            else:
                return page_, page_size_
        if page_size_ > max_page_size or page_size_ < 1:
            page_size_ = max_page_size
        return page_, page_size_

    def _handle_order_args(self, rison_args: Dict[str, Any]) -> Tuple[str, str]:
        """
        Help function to handle rison order
        arguments

        :param rison_args:
        :return:
        """
        order_column = rison_args.get(API_ORDER_COLUMN_RIS_KEY, "")
        order_direction = rison_args.get(API_ORDER_DIRECTION_RIS_KEY, "")
        if not order_column and self.base_order:
            return self.base_order
        if not order_column:
            return "", ""
        elif self.order_columns and order_column not in self.order_columns:
            raise InvalidOrderByColumnFABException(
                f"Invalid order by column: {order_column}"
            )
        return order_column, order_direction

    def _handle_filters_args(self, rison_args: Dict[str, Any]) -> Filters:
        self._filters.clear_filters()
        self._filters.rest_add_filters(rison_args.get(API_FILTERS_RIS_KEY, []))
        return self._filters.get_joined_filters(self._base_filters)

    def _description_columns_json(
        self, cols: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Prepares dict with col descriptions to be JSON serializable
        """
        ret = {}
        cols = cols or []
        d = {k: v for (k, v) in self.description_columns.items() if k in cols}
        for key, value in d.items():
            ret[key] = as_unicode(_(value).encode("UTF-8"))
        return ret

    def _get_field_info(
        self,
        field: Field,
        filter_rel_field: Dict[str, Any],
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Return a dict with field details
        ready to serve as a response

        :param field: marshmallow field
        :return: dict with field details
        """
        ret = {
            "name": field.name,
            "label": _(self.label_columns.get(field.name, "")),
            "description": _(self.description_columns.get(field.name, "")),
            "type": field.__class__.__name__,
            "required": field.required,
            # When using custom marshmallow schemas fields don't have unique property
            "unique": getattr(field, "unique", False),
        }
        # Handles related fields
        if isinstance(field, Related) or isinstance(field, RelatedList):
            ret["count"], ret["values"] = self._get_list_related_field(
                field, filter_rel_field, page=page, page_size=page_size
            )
        if field.validate and isinstance(field.validate, list):
            ret["validate"] = [str(v) for v in field.validate]
        elif field.validate:
            ret["validate"] = [str(field.validate)]
        return ret

    def _get_fields_info(
        self,
        cols: List[str],
        model_schema: Schema,
        filter_rel_fields: QueryRelatedFieldsFilters,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Returns a dict with fields detail
        from a marshmallow schema

        :param cols: list of columns to show info for
        :param model_schema: Marshmallow model schema
        :param filter_rel_fields: expects add_query_rel_fields or
                                    edit_query_rel_fields
        :param kwargs: Receives all rison arguments for pagination
        :return: dict with all fields details
        """
        ret = []
        for col in cols:
            page = page_size = None
            col_args = kwargs.get(col, {})
            if col_args:
                page = col_args.get(API_PAGE_INDEX_RIS_KEY, None)
                page_size = col_args.get(API_PAGE_SIZE_RIS_KEY, None)
            ret.append(
                self._get_field_info(
                    model_schema.fields[col],
                    filter_rel_fields.get(col, []),
                    page=page,
                    page_size=page_size,
                )
            )
        return ret

    def _get_list_related_field(
        self,
        field: Field,
        filter_rel_field: List[Any],
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Return a list of values for a related field

        :param field: Marshmallow field
        :param filter_rel_field: Filters for the related field,
                expects [field_name, Type[BaseFilter], value]
        :param page: The page index
        :param page_size: The page size
        :return: Total record count and list of dict with id and value
        """
        ret = []
        count = 0
        if isinstance(field, Related) or isinstance(field, RelatedList):
            datamodel = self.datamodel.get_related_interface(field.name)
            filters = datamodel.get_filters(datamodel.get_search_columns_list())
            page, page_size = self._sanitize_page_args(page, page_size)
            order_field = self.order_rel_fields.get(field.name)
            if order_field:
                order_column, order_direction = order_field
            else:
                order_column, order_direction = "", ""
            if filter_rel_field:
                filters = filters.add_filter_list(filter_rel_field)
            count, values = datamodel.query(
                filters, order_column, order_direction, page=page, page_size=page_size
            )
            for value in values:
                ret.append({"id": datamodel.get_pk_value(value), "value": str(value)})
        return count, ret

    def _merge_update_item(
        self, model_item: Model, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge a model with a python data structure
        This is useful to turn PUT method into a PATCH also
        """
        data_item = self.edit_model_schema.dump(model_item, many=False)
        for _col in self.edit_columns:
            if _col not in data.keys():
                data[_col] = data_item[_col]
        return data

    """
    ------------------------------------------------
                PRE AND POST METHODS
    ------------------------------------------------
    """

    def pre_update(self, item: Model) -> None:
        """
        Override this, this method is called before the update takes place.
        """
        pass

    def post_update(self, item: Model) -> None:
        """
        Override this, will be called after update
        """
        pass

    def pre_add(self, item: Model) -> None:
        """
        Override this, will be called before add.
        """
        pass

    def post_add(self, item: Model) -> None:
        """
        Override this, will be called after update
        """
        pass

    def pre_delete(self, item: Model) -> None:
        """
        Override this, will be called before delete
        """
        pass

    def post_delete(self, item: Model) -> None:
        """
        Override this, will be called after delete
        """
        pass

    def pre_get(self, data: Dict[str, Any]) -> None:
        """
        Override this, will be called before data is sent
        to the requester on get item endpoint.
        You can use it to mutate the response sent.
        Note that any new field added will not be reflected on the OpenApi spec.
        """
        pass

    def pre_get_list(self, data: Dict[str, Any]) -> None:
        """
        Override this, will be called before data is sent
        to the requester on get list endpoint.
        You can use it to mutate the response sent
        Note that any new field added will not be reflected on the OpenApi spec.
        """
        pass
