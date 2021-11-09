import datetime
from functools import reduce
import logging
from typing import Any, Type

from flask_babel import lazy_gettext

from .filters import BaseFilterConverter, Filters

try:
    import enum

    _has_enum = True
except ImportError:
    _has_enum = False

log = logging.getLogger(__name__)


class BaseInterface:
    """
    Base class for all data model interfaces.
    Sub class it to implement your own interface for some data engine.
    """

    filter_converter_class = Type[BaseFilterConverter]
    """ when sub classing override with your own custom filter converter """

    """ Messages to display on CRUD Events """
    add_row_message = lazy_gettext("Added Row")
    edit_row_message = lazy_gettext("Changed Row")
    delete_row_message = lazy_gettext("Deleted Row")
    delete_integrity_error_message = lazy_gettext(
        "Associated data exists, please delete them first"
    )
    add_integrity_error_message = lazy_gettext(
        "Integrity error, probably unique constraint"
    )
    edit_integrity_error_message = lazy_gettext(
        "Integrity error, probably unique constraint"
    )
    general_error_message = lazy_gettext("General Error")

    """ Tuple with message and text with severity type ex: ("Added Row", "info") """
    message = ()

    def __init__(self, obj: Type[Any]):
        self.obj = obj

    def __getattr__(self, name: str) -> Any:
        """
        Make mypy happy about the injected filters like self.datamodel.FilterEqual
        https://mypy.readthedocs.io/en/latest/cheat_sheet_py3.html#when-you-re-puzzled-or-when-things-are-complicated
        """
        return super().__getattr__(name)

    def _get_attr(self, col_name):
        if not hasattr(self.obj, col_name):
            # it's an inner obj attr
            try:
                _obj = self.obj
                for i in col_name.split("."):
                    try:
                        _obj = self.get_related_model(i)
                    except Exception:
                        _obj = getattr(_obj, i)
                return _obj
            except Exception:
                return None
        return getattr(self.obj, col_name)

    @staticmethod
    def _get_attr_value(item, col):
        if not hasattr(item, col):
            # it's an inner obj attr
            try:
                return reduce(getattr, col.split("."), item)
            except Exception:
                return ""
        if hasattr(getattr(item, col), "__call__"):
            # its a function
            return getattr(item, col)()
        else:
            # its an attribute
            value = getattr(item, col)
            # if value is an Enum instance than list and show widgets should display
            # its .value rather than its .name:
            if _has_enum and isinstance(value, enum.Enum):
                return value.value
            return value

    def get_filters(self, search_columns=None, search_filters=None):
        search_columns = search_columns or []
        return Filters(
            self.filter_converter_class,
            self,
            search_columns=search_columns,
            search_filters=search_filters,
        )

    def get_values_item(self, item, show_columns):
        return [self._get_attr_value(item, col) for col in show_columns]

    def _get_values(self, lst, list_columns):
        """
            Get Values: formats values for list template.
            returns [{'col_name':'col_value',....},{'col_name':'col_value',....}]

            :param lst:
                The list of item objects from query
            :param list_columns:
                The list of columns to include
        """
        retlst = []
        for item in lst:
            retdict = {}
            for col in list_columns:
                retdict[col] = self._get_attr_value(item, col)
            retlst.append(retdict)
        return retlst

    def get_values(self, lst, list_columns):
        """
            Get Values: formats values for list template.
            returns [{'col_name':'col_value',....},{'col_name':'col_value',....}]

            :param lst:
                The list of item objects from query
            :param list_columns:
                The list of columns to include
        """
        for item in lst:
            retdict = {}
            for col in list_columns:
                retdict[col] = self._get_attr_value(item, col)
            yield retdict

    def get_values_json(self, lst, list_columns):
        """
            Converts list of objects from query to JSON
        """
        result = []
        for item in self.get_values(lst, list_columns):
            for key, value in list(item.items()):
                if isinstance(value, datetime.datetime) or isinstance(
                    value, datetime.date
                ):
                    value = value.isoformat()
                    item[key] = value
                if isinstance(value, list):
                    item[key] = [str(v) for v in value]
            result.append(item)
        return result

    """
        Returns the models class name
        useful for auto title on views
    """

    @property
    def model_name(self):
        return self.obj.__class__.__name__

    """
        Next methods must be overridden
    """

    def query(
        self,
        filters=None,
        order_column="",
        order_direction="",
        page=None,
        page_size=None,
    ):
        pass

    def is_image(self, col_name):
        return False

    def is_file(self, col_name):
        return False

    def is_gridfs_file(self, col_name):
        return False

    def is_gridfs_image(self, col_name):
        return False

    def is_string(self, col_name):
        return False

    def is_text(self, col_name):
        return False

    def is_binary(self, col_name):
        return False

    def is_integer(self, col_name):
        return False

    def is_numeric(self, col_name):
        return False

    def is_float(self, col_name):
        return False

    def is_boolean(self, col_name):
        return False

    def is_date(self, col_name):
        return False

    def is_datetime(self, col_name):
        return False

    def is_enum(self, col_name):
        return False

    def is_relation(self, prop):
        return False

    def is_relation_col(self, col):
        return False

    def is_relation_many_to_one(self, prop):
        return False

    def is_relation_many_to_many(self, prop):
        return False

    def is_relation_one_to_one(self, prop):
        return False

    def is_relation_one_to_many(self, prop):
        return False

    def is_nullable(self, col_name):
        return True

    def is_unique(self, col_name):
        return False

    def is_pk(self, col_name):
        return False

    def is_pk_composite(self):
        raise False

    def is_fk(self, col_name):
        return False

    def get_max_length(self, col_name):
        return -1

    def get_min_length(self, col_name):
        return -1

    """
    -----------------------------------------
           FUNCTIONS FOR CRUD OPERATIONS
    -----------------------------------------
    """

    def add(self, item):
        """
            Adds object
        """
        raise NotImplementedError

    def edit(self, item):
        """
            Edit (change) object
        """
        raise NotImplementedError

    def delete(self, item):
        """
            Deletes object
        """
        raise NotImplementedError

    def get_col_default(self, col_name):
        pass

    def get_keys(self, lst):
        """
            return a list of pk values from object list
        """
        pk_name = self.get_pk_name()
        if self.is_pk_composite():
            return [[getattr(item, pk) for pk in pk_name] for item in lst]
        else:
            return [getattr(item, pk_name) for item in lst]

    def get_pk_name(self):
        """
            Returns the primary key name
        """
        raise NotImplementedError

    def get_pk_value(self, item):
        pk_name = self.get_pk_name()
        if self.is_pk_composite():
            return [getattr(item, pk) for pk in pk_name]
        else:
            return getattr(item, pk_name)

    def get(self, pk, filter=None):
        """
            return the record from key, you can optionally pass filters
            if pk exits on the db but filters exclude it it will return none.
        """
        pass

    def get_related_model(self, prop):
        raise NotImplementedError

    def get_related_interface(self, col_name):
        """
            Returns a BaseInterface for the related model
            of column name.

            :param col_name: Column name with relation
            :return: BaseInterface
        """
        raise NotImplementedError

    def get_related_obj(self, col_name, value):
        raise NotImplementedError

    def get_related_fk(self, model):
        raise NotImplementedError

    def get_columns_list(self):
        """
            Returns a list of all the columns names
        """
        return []

    def get_user_columns_list(self):
        """
            Returns a list of user viewable columns names
        """
        return self.get_columns_list()

    def get_search_columns_list(self):
        """
            Returns a list of searchable columns names
        """
        return []

    def get_order_columns_list(self, list_columns=None):
        """
            Returns a list of order columns names
        """
        return []

    def get_relation_fk(self, prop):
        pass
