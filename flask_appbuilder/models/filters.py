import copy
import logging
from typing import Any, Dict, List, Optional, Tuple, Type

from .._compat import as_unicode
from ..exceptions import (
    InvalidColumnFilterFABException,
    InvalidOperationFilterFABException,
)

log = logging.getLogger(__name__)

map_args_filter = {}
""" private map for arg_name and child Filter classes """


class BaseFilter(object):
    """
        Base class for all data filters.
        Sub class to implement your own custom filters
    """

    column_name = ""
    datamodel = None
    model = None
    name = ""
    is_related_view = False
    """
        Sets this filter to a special kind for related views.
        If true this filter was not set by the user
    """

    arg_name = None
    """
        the request argument that represent the filter
        child Filter classes should set it to enable
        REST API use
    """

    def __init__(self, column_name, datamodel, is_related_view=False):
        """
            Constructor.

            :param column_name:
                Model field name
            :param datamodel:
                The datamodel access class
            :param is_related_view:
                Optional internal parameter to filter related views
        """
        self.column_name = column_name
        self.datamodel = datamodel
        self.model = datamodel.obj
        self.is_related_view = is_related_view
        if self.arg_name:
            map_args_filter[self.arg_name] = self.__class__

    def apply(self, query, value):
        """
            Override this to implement your own new filters
        """
        raise NotImplementedError

    def __repr__(self):
        return self.name


class FilterRelation(BaseFilter):
    """
        Base class for all filters for relations
    """

    def apply(self, query, value):
        """
            Override this to implement your own new filters
        """
        raise NotImplementedError


class BaseFilterConverter:
    """
        Base Filter Converter, all classes responsible
        for the association of columns and possible filters
        will inherit from this and override the conversion_table property.

    """

    conversion_table = ()
    """
        When implementing your own filters you just need to define
        the new filters, and register them overriding this property.
        This will map a column type to all possible filters.
        use something like this::

            (
                ('is_text', [FilterCustomForText,
                         FilterNotContains,
                         FilterEqual,
                         FilterNotEqual]),
                ('is_string', [FilterContains,
                           FilterNotContains,
                           FilterEqual,
                           FilterNotEqual]),
                ('is_integer', [FilterEqual,
                            FilterNotEqual]),
            )

    """

    def __init__(self, datamodel):
        self.datamodel = datamodel

    def convert(self, col_name):
        for conversion in self.conversion_table:
            if getattr(self.datamodel, conversion[0])(col_name):
                return [item(col_name, self.datamodel) for item in conversion[1]]
        log.warning("Filter type not supported for column: %s", col_name)


class Filters(object):
    filters: List[BaseFilter] = []
    """ List of instantiated BaseFilter classes """
    values: List[Any] = []
    """ list of values to apply to filters """
    _search_filters: Dict[str, List[BaseFilter]] = {}
    """ dict like {'col_name':[BaseFilter1, BaseFilter2, ...], ... } """
    _all_filters: Dict[str, List[BaseFilter]] = {}

    def __init__(
        self,
        filter_converter: Type[BaseFilterConverter],
        datamodel,
        search_columns: Optional[List[str]] = None,
        search_filters: Optional[Dict[str, List[BaseFilter]]] = None,
    ):
        """

            :param filter_converter: Accepts BaseFilterConverter class
            :param search_columns: restricts possible columns,
                    accepts a list of column names
            :param search_filters: Add custom defined filters to specific columns
            :param datamodel: Accepts BaseInterface class
        """
        self.search_columns = search_columns or []
        self.filter_converter = filter_converter
        self.datamodel = datamodel
        self.clear_filters()
        if self.search_columns:
            self._search_filters = self._get_filters(self.search_columns)
        self._all_filters = self._get_filters(datamodel.get_columns_list())

        if search_filters:
            for k, v in search_filters.items():
                self._search_filters[k] += v

    def get_search_filters(self):
        return self._search_filters

    def _get_filters(self, cols: List[str]):
        filters = {}
        for col in cols:
            _filters = self.filter_converter(self.datamodel).convert(col)
            if _filters:
                filters[col] = _filters
        return filters

    def clear_filters(self):
        self.filters = []
        self.values = []

    def _add_filter(self, filter_instance, values):
        self.filters.append(filter_instance)
        self.values.append(values)

    def add_filter_index(
        self, column_name: str, filter_instance_index: int, value: Any
    ):
        if column_name in self._all_filters.keys():
            self._add_filter(
                self._all_filters[column_name][filter_instance_index], value
            )

    def rest_add_filters(self, data: List[Dict]) -> None:
        """
            Adds list of dicts

        :param data: list of dicts
        :return:
        """
        for _filter in data:
            try:
                opr = _filter["opr"]
                col = _filter["col"]
                value = _filter["value"]
            except KeyError:
                log.warning("Invalid filter")
                return
            # Get filter class from defaults
            filter_class = map_args_filter.get(opr, None)
            if filter_class:
                if col not in self.search_columns:
                    raise InvalidColumnFilterFABException(
                        f"Filter column: {col} not allowed to filter"
                    )
                elif not self._rest_check_valid_filter_operation(col, opr):
                    raise InvalidOperationFilterFABException(
                        f"Filter operation: {opr} not allowed on column: {col}"
                    )
                self.add_filter(col, filter_class, value)
                continue
            # Get filter class from custom defined filters
            filters = self._search_filters.get(col)
            if filters:
                for filter in filters:
                    if filter.arg_name == opr:
                        self.add_filter(col, filter, value)
                        break
            else:
                raise InvalidOperationFilterFABException(
                    f"Filter operation: {opr} not allowed on column: {col}"
                )

    def _rest_check_valid_filter_operation(self, col, opr):
        for filter_class in self._search_filters.get(col, []):
            if filter_class.arg_name == opr:
                return True
        return False

    def add_filter(self, column_name, filter_class, value):
        self._add_filter(filter_class(column_name, self.datamodel), value)
        return self

    def add_filter_related_view(self, column_name, filter_class, value):
        self._add_filter(filter_class(column_name, self.datamodel, True), value)
        return self

    def add_filter_list(self, active_filter_list=None):
        for item in active_filter_list:
            column_name, filter_class, value = item
            self._add_filter(filter_class(column_name, self.datamodel), value)
        return self

    def get_joined_filters(self, filters) -> "Filters":
        """
            Creates a new filters class with active filters joined
        """
        ret_filters = Filters(self.filter_converter, self.datamodel)
        ret_filters.filters = self.filters + filters.filters
        ret_filters.values = self.values + filters.values
        return ret_filters

    def copy(self):
        """
            Returns a copy of this object

            :return: A copy of self
        """
        retfilters = Filters(self.filter_converter, self.datamodel)
        retfilters.filters = copy.copy(self.filters)
        retfilters.values = copy.copy(self.values)
        return retfilters

    def get_relation_cols(self):
        """
            Returns the filter active FilterRelation cols
        """
        retlst = []
        for flt, value in zip(self.filters, self.values):
            if isinstance(flt, FilterRelation) and value:
                retlst.append(flt.column_name)
        return retlst

    def get_filters_values(self) -> List[Tuple[BaseFilter, Any]]:
        """
            Returns a list of tuples [(FILTER, value),(...,...),....]
        """
        return [(flt, value) for flt, value in zip(self.filters, self.values)]

    def get_filter_value(self, column_name: str) -> Any:
        """
            Returns the filtered value for a certain column

            :param column_name: The name of the column that we want the value from
            :return: the filter value of the column
        """
        for flt, value in zip(self.filters, self.values):
            if flt.column_name == column_name:
                return value

    def get_filters_values_tojson(self) -> List[Tuple[str, str, Any]]:
        return [
            (flt.column_name, as_unicode(flt.name), value)
            for flt, value in zip(self.filters, self.values)
        ]

    def apply_all(self, query):
        for flt, values in zip(self.filters, self.values):
            if isinstance(values, list):
                for value in values:
                    query = flt.apply(query, value)
            else:
                query = flt.apply(query, values)
        return query

    def __repr__(self):
        retstr = "FILTERS:"
        for flt, value in self.get_filters_values():
            retstr = retstr + "%s.%s:%s\n" % (
                flt.model.__table__,
                str(flt.column_name),
                str(value),
            )
        return retstr
