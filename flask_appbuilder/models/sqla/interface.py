# -*- coding: utf-8 -*-
import logging
import sys
from typing import List, Tuple

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased, Load
from sqlalchemy.orm.descriptor_props import SynonymProperty
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy_utils.types.uuid import UUIDType

from . import filters, Model
from ..base import BaseInterface
from ..group import GroupByCol, GroupByDateMonth, GroupByDateYear
from ..mixins import FileColumn, ImageColumn
from ..._compat import as_unicode
from ...const import (
    LOGMSG_ERR_DBI_ADD_GENERIC,
    LOGMSG_ERR_DBI_DEL_GENERIC,
    LOGMSG_ERR_DBI_EDIT_GENERIC,
    LOGMSG_WAR_DBI_ADD_INTEGRITY,
    LOGMSG_WAR_DBI_DEL_INTEGRITY,
    LOGMSG_WAR_DBI_EDIT_INTEGRITY,
)
from ...filemanager import FileManager, ImageManager
from ...utils.base import get_column_leaf, get_column_root_relation, is_column_dotted

log = logging.getLogger(__name__)


def _include_filters(obj):
    for key in filters.__all__:
        if not hasattr(obj, key):
            setattr(obj, key, getattr(filters, key))


def _is_sqla_type(obj, sa_type):
    return (
        isinstance(obj, sa_type)
        or isinstance(obj, sa.types.TypeDecorator)
        and isinstance(obj.impl, sa_type)
    )


class SQLAInterface(BaseInterface):
    """
    SQLAModel
    Implements SQLA support methods for views
    """

    session = None

    filter_converter_class = filters.SQLAFilterConverter

    def __init__(self, obj, session=None):
        _include_filters(self)
        self.list_columns = dict()
        self.list_properties = dict()

        self.session = session
        # Collect all SQLA columns and properties
        for prop in sa.orm.class_mapper(obj).iterate_properties:
            if type(prop) != SynonymProperty:
                self.list_properties[prop.key] = prop
        for col_name in obj.__mapper__.columns.keys():
            if col_name in self.list_properties:
                self.list_columns[col_name] = obj.__mapper__.columns[col_name]
        super(SQLAInterface, self).__init__(obj)

    @property
    def model_name(self):
        """
            Returns the models class name
            useful for auto title on views
        """
        return self.obj.__name__

    @staticmethod
    def is_model_already_joined(query, model):
        return model in [mapper.class_ for mapper in query._join_entities]

    def _get_base_query(
        self, query=None, filters=None, order_column="", order_direction=""
    ):
        if filters:
            query = filters.apply_all(query)
        if order_column != "":
            # if Model has custom decorator **renders('<COL_NAME>')**
            # this decorator will add a property to the method named *_col_name*
            if hasattr(self.obj, order_column):
                if hasattr(getattr(self.obj, order_column), "_col_name"):
                    order_column = getattr(self._get_attr(order_column), "_col_name")
            if order_direction == "asc":
                query = query.order_by(self._get_attr(order_column).asc())
            else:
                query = query.order_by(self._get_attr(order_column).desc())
        return query

    def _query_join_relation(self, query: BaseQuery, root_relation: str) -> BaseQuery:
        """
        Helper function that applies necessary joins for dotted columns on a
        SQLAlchemy query object

        :param query: SQLAlchemy query object
        :param root_relation: The root part of a dotted column, so the root relation
        :return: Transformed SQLAlchemy Query
        """
        relations = self.get_related_model_and_join(root_relation)

        for relation in relations:
            model_relation, relation_join = relation
            # Support multiple joins for the same table
            if self.is_model_already_joined(query, model_relation):
                # Since the join already exists apply a new aliased one
                model_relation = aliased(model_relation)
                # The binary expression needs to be inverted
                relation_join = BinaryExpression(
                    relation_join.left, model_relation.id, relation_join.operator
                )
            query = query.join(model_relation, relation_join, isouter=True)
        return query

    def _query_join_dotted_column(self, query: BaseQuery, column: str) -> BaseQuery:
        """

        :param query: SQLAlchemy query object
        :param column: If the column is dotted will join the root relation
        :return: Transformed SQLAlchemy Query
        """
        if is_column_dotted(column):
            return self._query_join_relation(query, get_column_root_relation(column))
        return query

    def _query_select_options(
        self, query: BaseQuery, select_columns: List[str] = None
    ) -> BaseQuery:
        """
        Add select load options to query. The goal
        is to only SQL select what is requested and join all the necessary
        models when dotted notation is used

        :param query: SQLAlchemy Query obj to apply joins and selects
        :param select_columns: (list) of columns
        :return: Transformed SQLAlchemy Query
        """
        if select_columns:
            load_options = list()
            joined_models = list()
            for column in select_columns:
                if is_column_dotted(column):
                    root_relation = get_column_root_relation(column)
                    leaf_column = get_column_leaf(column)
                    if root_relation not in joined_models:
                        query = self._query_join_relation(query, root_relation)
                        joined_models.append(root_relation)
                    load_options.append(
                        (
                            Load(self.obj)
                            .joinedload(root_relation)
                            .load_only(leaf_column)
                        )
                    )
                else:
                    # is a custom property method field?
                    if hasattr(getattr(self.obj, column), "fget"):
                        pass
                    # is not a relation and not a function?
                    elif not self.is_relation(column) and not hasattr(
                        getattr(self.obj, column), "__call__"
                    ):
                        load_options.append(Load(self.obj).load_only(column))
                    # it's a normal column
                    else:
                        load_options.append(Load(self.obj))
            query = query.options(*tuple(load_options))
        return query

    def query(
        self,
        filters=None,
        order_column="",
        order_direction="",
        page=None,
        page_size=None,
        select_columns=None,
    ):
        """
        Returns the results for a model query, applies filters, sorting and pagination

        :param filters:
            dict with filters {<col_name>:<value,...}
        :param order_column:
            name of the column to order
        :param order_direction:
            the direction to order <'asc'|'desc'>
        :param page:
            the current page
        :param page_size:
            the current page size
        """
        query = self.session.query(self.obj)
        query = self._query_join_dotted_column(query, order_column)
        query = self._query_select_options(query, select_columns)
        query_count = self.session.query(func.count("*")).select_from(self.obj)

        query_count = self._get_base_query(query=query_count, filters=filters)

        # MSSQL exception page/limit must have an order by
        if (
            page
            and page_size
            and not order_column
            and self.session.bind.dialect.name == "mssql"
        ):
            pk_name = self.get_pk_name()
            query = query.order_by(pk_name)

        query = self._get_base_query(
            query=query,
            filters=filters,
            order_column=order_column,
            order_direction=order_direction,
        )

        count = query_count.scalar()

        if page and page_size:
            query = query.offset(page * page_size)
        if page_size:
            query = query.limit(page_size)
        return count, query.all()

    def query_simple_group(
        self, group_by="", aggregate_func=None, aggregate_col=None, filters=None
    ):
        query = self.session.query(self.obj)
        query = self._get_base_query(query=query, filters=filters)
        query_result = query.all()
        group = GroupByCol(group_by, "Group by")
        return group.apply(query_result)

    def query_month_group(self, group_by="", filters=None):
        query = self.session.query(self.obj)
        query = self._get_base_query(query=query, filters=filters)
        query_result = query.all()
        group = GroupByDateMonth(group_by, "Group by Month")
        return group.apply(query_result)

    def query_year_group(self, group_by="", filters=None):
        query = self.session.query(self.obj)
        query = self._get_base_query(query=query, filters=filters)
        query_result = query.all()
        group_year = GroupByDateYear(group_by, "Group by Year")
        return group_year.apply(query_result)

    """
    -----------------------------------------
         FUNCTIONS for Testing TYPES
    -----------------------------------------
    """

    def is_image(self, col_name):
        try:
            return isinstance(self.list_columns[col_name].type, ImageColumn)
        except Exception:
            return False

    def is_file(self, col_name):
        try:
            return isinstance(self.list_columns[col_name].type, FileColumn)
        except Exception:
            return False

    def is_string(self, col_name):
        try:
            return (
                _is_sqla_type(self.list_columns[col_name].type, sa.types.String)
                or self.list_columns[col_name].type.__class__ == UUIDType
            )
        except Exception:
            return False

    def is_text(self, col_name):
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa.types.Text)
        except Exception:
            return False

    def is_binary(self, col_name):
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa.types.LargeBinary)
        except Exception:
            return False

    def is_integer(self, col_name):
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa.types.Integer)
        except Exception:
            return False

    def is_numeric(self, col_name):
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa.types.Numeric)
        except Exception:
            return False

    def is_float(self, col_name):
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa.types.Float)
        except Exception:
            return False

    def is_boolean(self, col_name):
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa.types.Boolean)
        except Exception:
            return False

    def is_date(self, col_name):
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa.types.Date)
        except Exception:
            return False

    def is_datetime(self, col_name):
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa.types.DateTime)
        except Exception:
            return False

    def is_enum(self, col_name):
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa.types.Enum)
        except Exception:
            return False

    def is_relation(self, col_name):
        try:
            return isinstance(
                self.list_properties[col_name], sa.orm.properties.RelationshipProperty
            )
        except Exception:
            return False

    def is_relation_many_to_one(self, col_name):
        try:
            if self.is_relation(col_name):
                return self.list_properties[col_name].direction.name == "MANYTOONE"
        except Exception:
            return False

    def is_relation_many_to_many(self, col_name):
        try:
            if self.is_relation(col_name):
                return self.list_properties[col_name].direction.name == "MANYTOMANY"
        except Exception:
            return False

    def is_relation_one_to_one(self, col_name):
        try:
            if self.is_relation(col_name):
                return self.list_properties[col_name].direction.name == "ONETOONE"
        except Exception:
            return False

    def is_relation_one_to_many(self, col_name):
        try:
            if self.is_relation(col_name):
                return self.list_properties[col_name].direction.name == "ONETOMANY"
        except Exception:
            return False

    def is_nullable(self, col_name):
        if self.is_relation_many_to_one(col_name):
            col = self.get_relation_fk(col_name)
            return col.nullable
        try:
            return self.list_columns[col_name].nullable
        except Exception:
            return False

    def is_unique(self, col_name):
        try:
            return self.list_columns[col_name].unique is True
        except Exception:
            return False

    def is_pk(self, col_name):
        try:
            return self.list_columns[col_name].primary_key
        except Exception:
            return False

    def is_pk_composite(self):
        return len(self.obj.__mapper__.primary_key) > 1

    def is_fk(self, col_name):
        try:
            return self.list_columns[col_name].foreign_keys
        except Exception:
            return False

    def get_max_length(self, col_name):
        try:
            if self.is_enum(col_name):
                return -1
            col = self.list_columns[col_name]
            if col.type.length:
                return col.type.length
            else:
                return -1
        except Exception:
            return -1

    """
    -------------------------------
     FUNCTIONS FOR CRUD OPERATIONS
    -------------------------------
    """

    def add(self, item, raise_exception=False):
        try:
            self.session.add(item)
            self.session.commit()
            self.message = (as_unicode(self.add_row_message), "success")
            return True
        except IntegrityError as e:
            self.message = (as_unicode(self.add_integrity_error_message), "warning")
            log.warning(LOGMSG_WAR_DBI_ADD_INTEGRITY.format(str(e)))
            self.session.rollback()
            if raise_exception:
                raise e
            return False
        except Exception as e:
            self.message = (
                as_unicode(self.general_error_message + " " + str(sys.exc_info()[0])),
                "danger",
            )
            log.exception(LOGMSG_ERR_DBI_ADD_GENERIC.format(str(e)))
            self.session.rollback()
            if raise_exception:
                raise e
            return False

    def edit(self, item, raise_exception=False):
        try:
            self.session.merge(item)
            self.session.commit()
            self.message = (as_unicode(self.edit_row_message), "success")
            return True
        except IntegrityError as e:
            self.message = (as_unicode(self.edit_integrity_error_message), "warning")
            log.warning(LOGMSG_WAR_DBI_EDIT_INTEGRITY.format(str(e)))
            self.session.rollback()
            if raise_exception:
                raise e
            return False
        except Exception as e:
            self.message = (
                as_unicode(self.general_error_message + " " + str(sys.exc_info()[0])),
                "danger",
            )
            log.exception(LOGMSG_ERR_DBI_EDIT_GENERIC.format(str(e)))
            self.session.rollback()
            if raise_exception:
                raise e
            return False

    def delete(self, item, raise_exception=False):
        try:
            self._delete_files(item)
            self.session.delete(item)
            self.session.commit()
            self.message = (as_unicode(self.delete_row_message), "success")
            return True
        except IntegrityError as e:
            self.message = (as_unicode(self.delete_integrity_error_message), "warning")
            log.warning(LOGMSG_WAR_DBI_DEL_INTEGRITY.format(str(e)))
            self.session.rollback()
            if raise_exception:
                raise e
            return False
        except Exception as e:
            self.message = (
                as_unicode(self.general_error_message + " " + str(sys.exc_info()[0])),
                "danger",
            )
            log.exception(LOGMSG_ERR_DBI_DEL_GENERIC.format(str(e)))
            self.session.rollback()
            if raise_exception:
                raise e
            return False

    def delete_all(self, items):
        try:
            for item in items:
                self._delete_files(item)
                self.session.delete(item)
            self.session.commit()
            self.message = (as_unicode(self.delete_row_message), "success")
            return True
        except IntegrityError as e:
            self.message = (as_unicode(self.delete_integrity_error_message), "warning")
            log.warning(LOGMSG_WAR_DBI_DEL_INTEGRITY.format(str(e)))
            self.session.rollback()
            return False
        except Exception as e:
            self.message = (
                as_unicode(self.general_error_message + " " + str(sys.exc_info()[0])),
                "danger",
            )
            log.exception(LOGMSG_ERR_DBI_DEL_GENERIC.format(str(e)))
            self.session.rollback()
            return False

    """
    -----------------------
     FILE HANDLING METHODS
    -----------------------
    """

    def _add_files(self, this_request, item):
        fm = FileManager()
        im = ImageManager()
        for file_col in this_request.files:
            if self.is_file(file_col):
                fm.save_file(this_request.files[file_col], getattr(item, file_col))
        for file_col in this_request.files:
            if self.is_image(file_col):
                im.save_file(this_request.files[file_col], getattr(item, file_col))

    def _delete_files(self, item):
        for file_col in self.get_file_column_list():
            if self.is_file(file_col):
                if getattr(item, file_col):
                    fm = FileManager()
                    fm.delete_file(getattr(item, file_col))
        for file_col in self.get_image_column_list():
            if self.is_image(file_col):
                if getattr(item, file_col):
                    im = ImageManager()
                    im.delete_file(getattr(item, file_col))

    """
    ------------------------------
     FUNCTIONS FOR RELATED MODELS
    ------------------------------
    """

    def get_col_default(self, col_name):
        default = getattr(self.list_columns[col_name], "default", None)
        if default is not None:
            value = getattr(default, "arg", None)
            if value is not None:
                if getattr(default, "is_callable", False):
                    return lambda: default.arg(None)
                else:
                    if not getattr(default, "is_scalar", True):
                        return None
                return value

    def get_related_model(self, col_name: str) -> Model:
        return self.list_properties[col_name].mapper.class_

    def get_related_model_and_join(self, col_name: str) -> List[Tuple[Model, object]]:
        relation = self.list_properties[col_name]
        if relation.direction.name == "MANYTOMANY":
            return [
                (relation.secondary, relation.primaryjoin),
                (relation.mapper.class_, relation.secondaryjoin),
            ]
        return [(relation.mapper.class_, relation.primaryjoin)]

    def query_model_relation(self, col_name):
        model = self.get_related_model(col_name)
        return self.session.query(model).all()

    def get_related_interface(self, col_name):
        return self.__class__(self.get_related_model(col_name), self.session)

    def get_related_obj(self, col_name, value):
        rel_model = self.get_related_model(col_name)
        return self.session.query(rel_model).get(value)

    def get_related_fks(self, related_views):
        return [view.datamodel.get_related_fk(self.obj) for view in related_views]

    def get_related_fk(self, model):
        for col_name in self.list_properties.keys():
            if self.is_relation(col_name):
                if model == self.get_related_model(col_name):
                    return col_name

    def get_info(self, col_name):
        if col_name in self.list_properties:
            return self.list_properties[col_name].info
        return {}

    """
    -------------
     GET METHODS
    -------------
    """

    def get_columns_list(self):
        """
            Returns all model's columns on SQLA properties
        """
        return list(self.list_properties.keys())

    def get_user_columns_list(self):
        """
            Returns all model's columns except pk or fk
        """
        ret_lst = list()
        for col_name in self.get_columns_list():
            if (not self.is_pk(col_name)) and (not self.is_fk(col_name)):
                ret_lst.append(col_name)
        return ret_lst

    # TODO get different solution, more integrated with filters
    def get_search_columns_list(self):
        ret_lst = list()
        for col_name in self.get_columns_list():
            if not self.is_relation(col_name):
                tmp_prop = self.get_property_first_col(col_name).name
                if (
                    (not self.is_pk(tmp_prop))
                    and (not self.is_fk(tmp_prop))
                    and (not self.is_image(col_name))
                    and (not self.is_file(col_name))
                ):
                    ret_lst.append(col_name)
            else:
                ret_lst.append(col_name)
        return ret_lst

    def get_order_columns_list(self, list_columns=None):
        """
            Returns the columns that can be ordered

            :param list_columns: optional list of columns name, if provided will
                use this list only.
        """
        ret_lst = list()
        list_columns = list_columns or self.get_columns_list()
        for col_name in list_columns:
            if not self.is_relation(col_name):
                if hasattr(self.obj, col_name):
                    if not hasattr(getattr(self.obj, col_name), "__call__") or hasattr(
                        getattr(self.obj, col_name), "_col_name"
                    ):
                        ret_lst.append(col_name)
                else:
                    ret_lst.append(col_name)
        return ret_lst

    def get_file_column_list(self):
        return [
            i.name
            for i in self.obj.__mapper__.columns
            if isinstance(i.type, FileColumn)
        ]

    def get_image_column_list(self):
        return [
            i.name
            for i in self.obj.__mapper__.columns
            if isinstance(i.type, ImageColumn)
        ]

    def get_property_first_col(self, col_name):
        # support for only one col for pk and fk
        return self.list_properties[col_name].columns[0]

    def get_relation_fk(self, col_name):
        # support for only one col for pk and fk
        return list(self.list_properties[col_name].local_columns)[0]

    def get(self, id, filters=None):
        if filters:
            query = self.session.query(self.obj)
            _filters = filters.copy()
            pk = self.get_pk_name()
            if self.is_pk_composite():
                for _pk, _id in zip(pk, id):
                    _filters.add_filter(_pk, self.FilterEqual, _id)
            else:
                _filters.add_filter(pk, self.FilterEqual, id)
            query = self._get_base_query(query=query, filters=_filters)
            return query.first()
        return self.session.query(self.obj).get(id)

    def get_pk_name(self):
        pk = [pk.name for pk in self.obj.__mapper__.primary_key]
        if pk:
            return pk if self.is_pk_composite() else pk[0]


"""
    For Retro-Compatibility
"""
SQLModel = SQLAInterface
