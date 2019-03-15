import re
import logging
import functools
from flask import Blueprint, abort, make_response, jsonify, request
from flask_babel import lazy_gettext as _
from .security.decorators import permission_name
from marshmallow import ValidationError
from ._compat import as_unicode

log = logging.getLogger(__name__)

URI_ORDER_BY_PREFIX = "_o_"
URI_PAGE_PREFIX = "_p_"
URI_FILTER_PREFIX = "_f_"
URI_SELECT_COL_PREFIX = "_c_"


def order_args(f):
    """
        Get order arguments decorator

        Arguments are passed like: _o_=<COL_NAME>:'<asc|desc>'
        
        function is called with named args: order_column, order_direction
    """
    def wraps(self, *args, **kwargs):
        orders = {}
        for arg, value in request.args.items():
            if arg == URI_ORDER_BY_PREFIX:
                re_match = re.findall('(.*):(.*)', value)
                for _item_re_match in re_match:
                    if _item_re_match and _item_re_match[1] in ('asc', 'desc'):
                        orders[_item_re_match[0]] = _item_re_match[1]
        if orders:
            for order_col, order_dir in orders.items():
                order_column, order_direction = order_col, order_dir
        else:
            order_column, order_direction = '', ''
        kwargs['order_column'] = order_column
        kwargs['order_direction'] = order_direction
        return f(self, *args,
                 order_column=order_column,
                 order_direction=order_direction)
    return functools.update_wrapper(wraps, f)


def page_args(f):
    """
        Get page arguments decorator

        Arguments are passed like: _p_=<SIZE>:'<INDEX>'

        function is called with named args: page_size, page_index
    """
    def wraps(self, *args, **kwargs):
        for arg, value in request.args.items():
            if arg == URI_PAGE_PREFIX:
                re_match = re.findall('(.*):(.*)', value)
                for _item_re_match in re_match:
                    if _item_re_match and len(_item_re_match) == 2:
                        try:
                            kwargs['page_size'] = int(_item_re_match[0])
                            kwargs['page_index'] = int(_item_re_match[1])
                            return f(self, *args, **kwargs)
                        except ValueError:
                            log.warning("Bad page args {}, {}".format(
                                _item_re_match[0],
                                _item_re_match[1])
                            )
        kwargs['page_size'] = self.page_size
        kwargs['page_index'] = 0
        return f(self, *args, **kwargs)
    return functools.update_wrapper(wraps, f)


def select_col_args(f):
    """
        Get selectable columns on the fly

        Arguments are passed like: _c_=<COL_NAME>,<COL_NAME>, ...

        function is called with named args: page_size, page_index
    """
    def wraps(self, *args, **kwargs):
        for arg, value in request.args.items():
            if arg == URI_SELECT_COL_PREFIX:
                re_match = re.findall('(\w+),*', value)
                kwargs['select_cols'] = [i for i in re_match]
        return f(self, *args, **kwargs)
    return functools.update_wrapper(wraps, f)


def filter_args(f):
    """
        Get filter arguments, return a list of dicts
        { <VIEW_NAME>: (ORDER_COL, ORDER_DIRECTION) }

        Arguments are passed like: _f_<INDEX>=<COL_NAME>:<OPERATOR>:<VALUE>

        :return: list [
                        {
                            "col_name":"<COLNAME>",
                            "operator":"<operator>",
                            "value":"<value>",                            
                        }
                      ]
    """
    def wraps(self, *args, **kwargs):
        filters = list()
        for arg, value in request.args.items():
            key_match = re.match(r"{}(\d)".format(URI_FILTER_PREFIX), arg)
            if key_match:
                re_match = re.findall('(.*):(.*):(.*)', value)
                for _item_re_match in re_match:
                    if _item_re_match and len(_item_re_match) == 3:
                        filters.append({"col_name": _item_re_match[0],
                                        "operator": _item_re_match[1],
                                        "value": _item_re_match[2],
                                        })
                    else:
                        log.warning("Bar filter args {} ".format(_item_re_match))
        kwargs['filters'] = filters
        return f(self, *args, **kwargs)
    return functools.update_wrapper(wraps, f)


def expose(url='/', methods=('GET',)):
    """
        Use this decorator to expose views on your view classes.

        :param url:
            Relative URL for the view
        :param methods:
            Allowed HTTP methods. By default only GET is allowed.
    """

    def wrap(f):
        if not hasattr(f, '_urls'):
            f._urls = []
        f._urls.append((url, methods))
        return f
    return wrap


class BaseApi:
    """
        All apis inherit from this class.
        it's constructor will register your exposed urls on flask
        as a Blueprint.

        This class does not expose any urls, 
        but provides a common base for all apis.
    """

    appbuilder = None
    blueprint = None
    endpoint = None

    version = 'v1'
    route_base = None

    base_permissions = None
    extra_args = None

    def __init__(self):
        """
            Initialization of base permissions
            based on exposed methods and actions

            Initialization of extra args
        """
        if self.base_permissions is None:
            self.base_permissions = set()
            for attr_name in dir(self):
                if hasattr(getattr(self, attr_name), '_permission_name'):
                    _permission_name = \
                        getattr(getattr(self, attr_name), '_permission_name')
                    self.base_permissions.add('can_' + _permission_name)
            self.base_permissions = list(self.base_permissions)
        if not self.extra_args:
            self.extra_args = dict()
        self._apis = dict()
        for attr_name in dir(self):
            if hasattr(getattr(self, attr_name), '_extra'):
                _extra = getattr(getattr(self, attr_name), '_extra')
                for key in _extra: self._apis[key] = _extra[key]

    def create_blueprint(self, appbuilder,
                         endpoint=None,
                         static_folder=None):
        # Store appbuilder instance
        self.appbuilder = appbuilder
        # If endpoint name is not provided, get it from the class name
        self.endpoint = endpoint or self.__class__.__name__

        if self.route_base is None:
            self.route_base = \
                "/api/{}/{}".format(self.version,
                                    self.__class__.__name__.lower())
        self.blueprint = Blueprint(self.endpoint, __name__,
                                   url_prefix=self.route_base)

        self._register_urls()
        return self.blueprint

    def _register_urls(self):
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, '_urls'):
                for url, methods in attr._urls:
                    self.blueprint.add_url_rule(url,
                                                attr_name,
                                                attr,
                                                methods=methods)

    @staticmethod
    def _prettify_name(name):
        """
            Prettify pythonic variable name.

            For example, 'HelloWorld' will be converted to 'Hello World'

            :param name:
                Name to prettify.
        """
        return re.sub(r'(?<=.)([A-Z])', r' \1', name)

    @staticmethod
    def _prettify_column(name):
        """
            Prettify pythonic variable name.

            For example, 'hello_world' will be converted to 'Hello World'

            :param name:
                Name to prettify.
        """
        return re.sub('[._]', ' ', name).title()

    def get_uninit_inner_views(self):
        """
            Will return a list with views that need to be initialized.
            Normally related_views from ModelView
        """
        return []

    def get_init_inner_views(self, views):
        """
            Sets initialized inner views
        """
        pass


class BaseModelApi(BaseApi):
    datamodel = None
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

            class MyView(ModelView):
                datamodel = SQLAInterface(MyTable)
                search_columns = ['name', 'address']

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

            class MyView(ModelApi):
                datamodel = SQLAInterface(MyTable)
                label_columns = {'name':'My Name Label Override'}

    """
    base_filters = None
    """
        Filter the view use: [['column_name',BaseFilter,'value'],]

        example::

            def get_user():
                return g.user

            class MyView(ModelApi):
                datamodel = SQLAInterface(MyTable)
                base_filters = [['created_by', FilterEqualFunction, get_user],
                                ['name', FilterStartsWith, 'a']]

    """

    base_order = None
    """
        Use this property to set default ordering for lists
         ('col_name','asc|desc')::

            class MyView(ModelApi):
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
    list_model_schema = None
    add_model_schema = None
    edit_model_schema = None
    show_model_schema = None

    def __init__(self, **kwargs):
        """
            Constructor
        """
        datamodel = kwargs.get('datamodel', None)
        if datamodel:
            self.datamodel = datamodel
        self._init_properties()
        self._init_titles()
        super(BaseModelApi, self).__init__()

    def _gen_labels_columns(self, list_columns):
        """
            Auto generates pretty label_columns from list of columns
        """
        for col in list_columns:
            if not self.label_columns.get(col):
                self.label_columns[col] = self._prettify_column(col)

    def _label_columns_json(self, cols=None):
        """
            Prepares dict with labels to be JSON serializable
        """
        ret = {}
        cols = cols or []
        d = {k: v for (k, v) in self.label_columns.items() if k in cols}
        for key, value in d.items():
            ret[key] = as_unicode(_(value).encode('UTF-8'))
        return ret

    def _init_properties(self):
        self.label_columns = self.label_columns or {}
        self.base_filters = self.base_filters or []
        self.search_exclude_columns = self.search_exclude_columns or []
        self.search_columns = self.search_columns or []

        self._base_filters = self.datamodel.get_filters().add_filter_list(self.base_filters)
        list_cols = self.datamodel.get_columns_list()
        search_columns = self.datamodel.get_search_columns_list()
        if not self.search_columns:
            self.search_columns = \
                [x for x in search_columns if x not in self.search_exclude_columns]

        self._gen_labels_columns(list_cols)
        self._filters = self.datamodel.get_filters(self.search_columns)

    def _init_titles(self):
        pass


class ModelApi(BaseModelApi):
    list_title = ""
    """ 
        List Title, if not configured the default is 
        'List ' with pretty model name 
    """
    show_title = ""
    """
        Show Title , if not configured the default is 
        'Show ' with pretty model name 
    """
    add_title = ""
    """ 
        Add Title , if not configured the default is 
        'Add ' with pretty model name
    """
    edit_title = ""
    """ 
        Edit Title , if not configured the default is 
        'Edit ' with pretty model name
    """

    list_columns = None
    """
        A list of columns (or model's methods) to be displayed on the list view.
        Use it to control the order of the display
    """
    show_columns = None
    """
        A list of columns (or model's methods) to be displayed on the show view.
        Use it to control the order of the display
    """
    add_columns = None
    """
        A list of columns (or model's methods) to be displayed 
        on the add form view. Use it to control the order of the display
    """
    edit_columns = None
    """
        A list of columns (or model's methods) to be displayed 
        on the edit form view. Use it to control the order of the display
    """
    show_exclude_columns = None
    """
        A list of columns to exclude from the show view. 
        By default all columns are included.
    """
    add_exclude_columns = None
    """
        A list of columns to exclude from the add form.
        By default all columns are included.
    """
    edit_exclude_columns = None
    """
        A list of columns to exclude from the edit form.
        By default all columns are included.
    """
    order_columns = None
    """ Allowed order columns """
    page_size = 10
    """
        Use this property to change default page size
    """
    description_columns = None
    """
        Dictionary with column descriptions that will be shown on the forms::

            class MyView(ModelView):
                datamodel = SQLAModel(MyTable, db.session)

                description_columns = {'name':'your models name column',
                                        'address':'the address column'}
    """
    formatters_columns = None
    """ Dictionary of formatter used to format the display of columns

        formatters_columns = {'some_date_col': lambda x: x.isoformat() }
    """
    add_query_rel_fields = None
    """
        Add Customized query for related add fields.
        Assign a dictionary where the keys are the column names of
        the related models to filter, the value for each key, is a list of lists with the
        same format as base_filter
        {'relation col name':[['Related model col',FilterClass,'Filter Value'],...],...}
        Add a custom filter to form related fields::
    
            class ContactModelView(ModelView):
                datamodel = SQLAModel(Contact, db.session)
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
    
            class ContactModelView(ModelView):
                datamodel = SQLAModel(Contact, db.session)
                edit_query_rel_fields = {'group':[['name',FilterStartsWith,'W']]}
    
    """

    def create_blueprint(self, appbuilder, *args, **kwargs):
        self._init_model_schemas()
        return super(ModelApi, self).create_blueprint(appbuilder,
                                                      *args, **kwargs)

    def _init_model_schemas(self):
        # Create Marshmalow schemas if one is not specified
        if self.list_model_schema is None:
            self.list_model_schema = \
                self._model_schema_factory(self.list_columns)
        if self.add_model_schema is None:
            self.add_model_schema = \
                self._model_schema_factory(self.add_columns)
        if self.edit_model_schema is None:
            self.edit_model_schema = \
                self._model_schema_factory(self.edit_columns)
        if self.show_model_schema is None:
            self.show_model_schema = \
                self._model_schema_factory(self.show_columns)

    def _model_schema_factory(self, columns):
        """
            Will create a Marshmallow SQLAlchemy schema class
        :param columns: List with columns to include
        :return: ModelSchema object
        """
        class MetaSchema(self.appbuilder.marshmallow.ModelSchema):
            class Meta:
                model = self.datamodel.obj
                fields = columns
                strict = True
        return MetaSchema()

    def _init_titles(self):
        """
            Init Titles if not defined
        """
        super(ModelApi, self)._init_titles()
        class_name = self.datamodel.model_name
        if not self.list_title:
            self.list_title = 'List ' + self._prettify_name(class_name)
        if not self.add_title:
            self.add_title = 'Add ' + self._prettify_name(class_name)
        if not self.edit_title:
            self.edit_title = 'Edit ' + self._prettify_name(class_name)
        if not self.show_title:
            self.show_title = 'Show ' + self._prettify_name(class_name)
        self.title = self.list_title

    def _init_properties(self):
        """
            Init Properties
        """
        super(ModelApi, self)._init_properties()
        # Reset init props
        self.description_columns = self.description_columns or {}
        self.formatters_columns = self.formatters_columns or {}
        self.show_exclude_columns = self.show_exclude_columns or []
        self.add_exclude_columns = self.add_exclude_columns or []
        self.edit_exclude_columns = self.edit_exclude_columns or []
        # Generate base props
        list_cols = self.datamodel.get_user_columns_list()
        if not self.list_columns and self.list_model_schema:
            self.list_columns =\
                list(self.list_model_schema._declared_fields.keys())
        else:
            self.list_columns = self.list_columns or \
                                self.datamodel.get_columns_list()
        self._gen_labels_columns(self.list_columns)
        self.order_columns = self.order_columns or \
            self.datamodel.get_order_columns_list(list_columns=self.list_columns)
        # Process excluded columns
        if not self.show_columns:
            self.show_columns = \
                [x for x in list_cols if x not in self.show_exclude_columns]
        if not self.add_columns:
            self.add_columns = \
                [x for x in list_cols if x not in self.add_exclude_columns]
        if not self.edit_columns:
            self.edit_columns = \
                [x for x in list_cols if x not in self.edit_exclude_columns]
        self._filters = self.datamodel.get_filters(self.search_columns)
        self.edit_query_rel_fields = self.edit_query_rel_fields or dict()
        self.add_query_rel_fields = self.add_query_rel_fields or dict()

    def _get_field_info(self, field, filter_rel_field):
        """
            Return a dict with field details
            ready to serve as a response

        :param field: marshmallow field
        :return: dict with field details
        """
        from marshmallow_sqlalchemy.fields import Related, RelatedList
        ret = dict()
        ret['name'] = field.name
        ret['label'] = self.label_columns.get(field.name, '')
        ret['description'] = self.description_columns.get(field.name, '')
        # Handles related fields
        if isinstance(field, Related) or isinstance(field, RelatedList):
            _rel_interface = self.datamodel.get_related_interface(field.name)
            _filters = _rel_interface .get_filters(_rel_interface .get_search_columns_list())
            if filter_rel_field:
                filters = _filters.add_filter_list(filter_rel_field)
                _values = _rel_interface.query(filters)[1]
            else:
                _values = _rel_interface.query()[1]
            ret['values'] = list()
            for _value in _values:
                ret['values'].append(
                    {
                        "id": _rel_interface.get_pk_value(_value),
                        "value": str(_value)
                    }
                )

        if field.validate:
            ret['validate'] = [str(v) for v in field.validate]
        ret['type'] = field.__class__.__name__
        ret['required'] = field.required
        return ret

    def _get_fields_info(self, cols, model_schema, filter_rel_fields):
        """
            Returns a dict with fields detail
            from a marshmallow schema

        :param cols: list of columns to show info for
        :param model_schema: Marshmallow model schema
        :param filter_rel_fields: expects add_query_rel_fields or
                                    edit_query_rel_fields
        :return: dict with all fields details
        """
        return [
            self._get_field_info(
                model_schema.fields[col],
                filter_rel_fields.get(col, [])
            )
            for col in cols
        ]

    @expose('/info', methods=['GET'])
    @permission_name('get')
    def info(self):
        # Get info from add fields
        _add_fields = self._get_fields_info(
            self.add_columns,
            self.add_model_schema,
            self.add_query_rel_fields
        )
        # Get info from edit fields
        _edit_fields = self._get_fields_info(
            self.edit_columns,
            self.edit_model_schema,
            self.edit_query_rel_fields
        )

        # Get possible search fields and all possible operations
        search_filters = dict()
        dict_filters = self._filters.get_search_filters()
        for col in self.search_columns:
            search_filters[col] = [
                {'name': as_unicode(flt.name),
                 'operator': flt.arg_name} for flt in dict_filters[col]
            ]
        return self._api_json_response(
            200,
            filters=search_filters,
            add_fields=_add_fields,
            edit_fields=_edit_fields
        )

    @expose('/', methods=['GET'])
    @expose('/<pk>/', methods=['GET'])
    @permission_name('get')
    def get(self, pk=None):
        if not pk:
            return self._get_list()
        return self._get_item(pk)

    @expose('/', methods=['POST'])
    @permission_name('post')
    def post(self):
        try:
            item = self.add_model_schema.load(request.json)
        except ValidationError as err:
            return self._api_json_response(400, **{'message': err.messages})
        else:
            self.pre_add(item.data)
            if self.datamodel.add(item.data):
                self.post_add(item.data)
                return self._api_json_response(
                    201,
                    **{'result': self.add_model_schema.dump(item.data, many=False).data}
                )
            else:
                return self._api_json_500()

    @expose('/<pk>', methods=['PUT'])
    @permission_name('put')
    def put(self, pk):
        item = self.datamodel.get(pk, self._base_filters)
        if not item:
            return self._api_json_404()
        else:
            try:
                item = self.edit_model_schema.load(request.json, instance=item)
            except ValidationError as err:
                return self._api_json_response(400, **{'message': err.messages})
            else:
                self.pre_update(item.data)
                if self.datamodel.edit(item.data):
                    self.post_add(item)
                    self.post_update(item)
                    return self._api_json_response(
                        200,
                        **{'result': self.edit_model_schema.dump(item.data, many=False).data}
                    )
                else:
                    return self._api_json_500()

    @expose('/<pk>', methods=['DELETE'])
    @permission_name('delete')
    def delete(self, pk):
        item = self.datamodel.get(pk, self._base_filters)
        if not item:
            return self._api_json_404()
        else:
            self.pre_delete(item)
            if self.datamodel.delete(item):
                self.post_delete(item)
                return self._api_json_response(200, **{'message': 'OK'})
            else:
                return self._api_json_500()

    @select_col_args
    def _get_item(self, pk, select_cols=None):
        item = self.datamodel.get(pk, self._base_filters)
        if not item:
            return self._api_json_404()
        select_cols = select_cols or []
        _pruned_select_cols = [col for col in select_cols if col in self.show_columns]
        if _pruned_select_cols:
            _show_columns = _pruned_select_cols
            _show_model_schema = self._model_schema_factory(_pruned_select_cols)
        else:
            _show_columns = self.show_columns
            _show_model_schema = self.show_model_schema
        return self._api_json_response(
            200, pk=pk,
            label_columns=self._label_columns_json(_show_columns),
            include_columns=_show_columns,
            description_columns=self._description_columns_json(_show_columns),
            modelview_name=self.__class__.__name__,
            result=_show_model_schema.dump(item, many=False).data
        )

    @order_args
    @page_args
    @filter_args
    @select_col_args
    def _get_list(self, filters=None, order_column=None, order_direction=None,
                  page_size=0, page_index=0, select_cols=None):

        # handle select columns
        select_cols = select_cols or []
        _pruned_select_cols = [col for col in select_cols if col in self.list_columns]
        if _pruned_select_cols:
            _list_columns = _pruned_select_cols
            _list_model_schema = self._model_schema_factory(_pruned_select_cols)
        else:
            _list_columns = self.list_columns
            _list_model_schema = self.list_model_schema
        # handle filters
        self._filters.clear_filters()
        self._filters.rest_add_filters(filters)
        joined_filters = self._filters.get_joined_filters(self._base_filters)
        # handle base order
        if not order_column and self.base_order:
            order_column, order_direction = self.base_order
        # Make the query
        count, lst = self.datamodel.query(joined_filters,
                                          order_column,
                                          order_direction,
                                          page=page_index,
                                          page_size=page_size)
        pks = self.datamodel.get_keys(lst)
        order_columns = [
            order_col
            for order_col in self.order_columns if order_col in _list_columns
        ]
        return self._api_json_response(
            200,
            label_columns=self._label_columns_json(_list_columns),
            list_columns=_list_columns,
            description_columns=self._description_columns_json(_list_columns),
            order_columns=order_columns,
            modelview_name=self.__class__.__name__,
            count=count,
            ids=pks,
            result=_list_model_schema.dump(lst, many=True).data
        )
    """
    ------------------------------------------------
                HELPER FUNCTIONS
    ------------------------------------------------
    """
    @staticmethod
    def _api_json_response(code, **kwargs):
        _ret_json = jsonify(kwargs)
        response = make_response(_ret_json, code)
        response.headers['Content-Type'] = "application/json; charset=utf-8"
        return response

    def _api_json_404(self):
        return self._api_json_response(404, **{"message": "Not found"})

    def _api_json_500(self, message=None):
        message = message or "Internal error"
        return self._api_json_response(500, **{"message": message})

    def _description_columns_json(self, cols=None):
        """
            Prepares dict with col descriptions to be JSON serializable
        """
        ret = {}
        cols = cols or []
        d = {k: v for (k, v) in self.description_columns.items() if k in cols}
        for key, value in d.items():
            ret[key] = as_unicode(_(value).encode('UTF-8'))
        return ret

    def pre_update(self, item):
        """
            Override this, this method is called before the update takes place.
            If an exception is raised by this method,
            the message is shown to the user and the update operation is
            aborted. Because of this behavior, it can be used as a way to
            implement more complex logic around updates. For instance
            allowing only the original creator of the object to update it.
        """
        pass

    def post_update(self, item):
        """
            Override this, will be called after update
        """
        pass

    def pre_add(self, item):
        """
            Override this, will be called before add.
            If an exception is raised by this method,
            the message is shown to the user and the add operation is aborted.
        """
        pass

    def post_add(self, item):
        """
            Override this, will be called after update
        """
        pass

    def pre_delete(self, item):
        """
            Override this, will be called before delete
            If an exception is raised by this method,
            the message is shown to the user and the delete operation is
            aborted. Because of this behavior, it can be used as a way to
            implement more complex logic around deletes. For instance
            allowing only the original creator of the object to delete it.
        """
        pass

    def post_delete(self, item):
        """
            Override this, will be called after delete
        """
        pass
