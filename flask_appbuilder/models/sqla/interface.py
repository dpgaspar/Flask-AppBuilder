# -*- coding: utf-8 -*-
from contextlib import suppress
import logging
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from flask_appbuilder._compat import as_unicode
from flask_appbuilder.const import (
    LOGMSG_ERR_DBI_DEL_GENERIC,
    LOGMSG_WAR_DBI_ADD_INTEGRITY,
    LOGMSG_WAR_DBI_DEL_INTEGRITY,
    LOGMSG_WAR_DBI_EDIT_INTEGRITY,
)
from flask_appbuilder.exceptions import InterfaceQueryWithoutSession
from flask_appbuilder.filemanager import FileManager, ImageManager
from flask_appbuilder.models.base import BaseInterface
from flask_appbuilder.models.filters import Filters
from flask_appbuilder.models.group import GroupByCol, GroupByDateMonth, GroupByDateYear
from flask_appbuilder.models.mixins import FileColumn, ImageColumn
from flask_appbuilder.models.sqla import filters, Model
from flask_appbuilder.utils.base import (
    get_column_leaf,
    get_column_root_relation,
    is_column_dotted,
)
from sqlalchemy import asc, desc
from sqlalchemy import types as sa_types
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased, class_mapper, ColumnProperty, contains_eager, Load
from sqlalchemy.orm.descriptor_props import SynonymProperty
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session as SessionBase
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql import visitors
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.sqltypes import TypeEngine
from sqlalchemy_utils.types.uuid import UUIDType

log = logging.getLogger(__name__)


def _is_sqla_type(model: Model, sa_type: Type[TypeEngine]) -> bool:
    return (
        isinstance(model, sa_type)
        or isinstance(model, sa_types.TypeDecorator)
        and isinstance(model.impl, sa_type)
    )


class SQLAInterface(BaseInterface):
    """
    SQLAModel
    Implements SQLA support methods for views
    """

    filter_converter_class = filters.SQLAFilterConverter

    def __init__(self, obj: Type[Model], session: Optional[SessionBase] = None) -> None:
        _include_filters(self)
        self.list_columns = dict()
        self.list_properties = dict()
        self.session = session
        # Collect all SQLA columns and properties
        for prop in class_mapper(obj).iterate_properties:
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
    def is_model_already_joined(query: Query, model: Type[Model]) -> bool:
        if hasattr(query, "_join_entities"):  # For SQLAlchemy < 1.3
            return model in [mapper.class_ for mapper in query._join_entities]
        # Solution for SQLAlchemy >= 1.4
        model_table_name = model.__table__.fullname
        for visitor in visitors.iterate(query.statement):
            # Checking for `.join(Parent.child)` clauses
            if visitor.__visit_name__ == "alias":
                _visitor = visitor.element
            else:
                _visitor = visitor
            if _visitor.__visit_name__ == "select":
                continue
            if _visitor.__visit_name__ == "binary":
                for vis in visitors.iterate(_visitor):
                    # Visitor might not have table attribute
                    with suppress(AttributeError):
                        # Verify if already present based on table name
                        if model_table_name == vis.table.fullname:
                            return True
            # Checking for `.join(Child)` clauses
            if _visitor.__visit_name__ == "table":
                # Visitor might be of ColumnCollection or so,
                # which cannot be compared to model
                if model_table_name == _visitor.fullname:
                    return True
            # Checking for `Model.column` clauses
            if _visitor.__visit_name__ == "column":
                with suppress(AttributeError):
                    if model_table_name == _visitor.table.fullname:
                        return True
        return False

    def _get_base_query(
        self, query=None, filters=None, order_column="", order_direction=""
    ):
        if filters:
            query = filters.apply_all(query)
        return self.apply_order_by(query, order_column, order_direction)

    def _query_join_relation(
        self,
        query: Query,
        root_relation: str,
        aliases_mapping: Dict[str, AliasedClass] = None,
    ) -> Query:
        """
        Helper function that applies necessary joins for dotted columns on a
        SQLAlchemy query object

        :param query: SQLAlchemy query object
        :param root_relation: The root part of a dotted column, so the root relation
        :return: Transformed SQLAlchemy Query
        """
        if aliases_mapping is None:
            aliases_mapping = {}
        relations = self.get_related_model_and_join(root_relation)

        for relation in relations:
            model_relation, relation_join = relation
            # Use alias if it's not a custom relation
            if not hasattr(relation_join, "clauses"):
                model_relation = aliased(model_relation, name=root_relation)
                aliases_mapping[root_relation] = model_relation
                relation_pk = self.get_pk(model_relation)
                if relation_join.left.foreign_keys:
                    relation_join = BinaryExpression(
                        relation_join.left, relation_pk, relation_join.operator
                    )
                else:
                    relation_join = BinaryExpression(
                        relation_join.right, relation_pk, relation_join.operator
                    )
            query = query.join(model_relation, relation_join, isouter=True)
        return query

    def apply_engine_specific_hack(
        self,
        query: Query,
        page: Optional[int],
        page_size: Optional[int],
        order_column: Optional[str],
    ) -> Query:
        # MSSQL exception page/limit must have an order by
        if (
            page
            and page_size
            and not order_column
            and self.session.bind.dialect.name == "mssql"
        ):
            pk_name = self.get_pk_name()
            return query.order_by(pk_name)
        return query

    def apply_order_by(
        self,
        query: Query,
        order_column: str,
        order_direction: str,
        aliases_mapping: Dict[str, AliasedClass] = None,
        add_pk: bool = False,
    ) -> Query:
        if order_column != "":
            # if Model has custom decorator **renders('<COL_NAME>')**
            # this decorator will add a property to the method named *_col_name*
            if hasattr(self.obj, order_column):
                if hasattr(getattr(self.obj, order_column), "_col_name"):
                    order_column = getattr(self._get_attr(order_column), "_col_name")
            _order_column = self._get_attr(order_column) or order_column

            if is_column_dotted(order_column):
                root_relation = get_column_root_relation(order_column)
                # On MVC we still allow for joins to happen here
                if not self.is_model_already_joined(
                    query, self.get_related_model(root_relation)
                ):
                    query = self._query_join_relation(
                        query, root_relation, aliases_mapping=aliases_mapping
                    )
                column_leaf = get_column_leaf(order_column)
                _alias = self.get_alias_mapping(root_relation, aliases_mapping)
                _order_column = getattr(_alias, column_leaf)
            # get the primary key so we can add a tie breaker of the order
            # when the order column is not unique it can cause issues with pagination
            direction = asc if order_direction == "asc" else desc
            order_by_columns = [direction(_order_column)]
            pk = self.get_pk()
            if add_pk and pk and pk != _order_column:
                order_by_columns.append(direction(pk))
            query = query.order_by(*order_by_columns)

        return query

    def apply_pagination(
        self, query: Query, page: Optional[int], page_size: Optional[int]
    ) -> Query:
        if page and page_size:
            query = query.offset(page * page_size)
        if page_size:
            query = query.limit(page_size)
        return query

    def apply_filters(self, query: Query, filters: Optional[Filters]) -> Query:
        if filters:
            return filters.apply_all(query)
        return query

    def _apply_normal_col_select_option(self, query: Query, column: str) -> Query:
        if not self.is_relation(column) and not self.is_property_or_function(column):
            return query.options(Load(self.obj).load_only(column))
        return query

    def _apply_relation_fks_select_options(self, query: Query, relation_name) -> Query:
        relation = getattr(self.obj, relation_name)
        if hasattr(relation, "property"):
            local_cols = getattr(self.obj, relation_name).property.local_columns
            for local_fk in local_cols:
                query = query.options(Load(self.obj).load_only(local_fk.name))
            return query
        return query

    def apply_inner_select_joins(
        self,
        query: Query,
        select_columns: List[str] = None,
        aliases_mapping: Dict[str, AliasedClass] = None,
    ) -> Query:
        """
        Add select load options to query. The goal
        is to only SQL select what is requested and join all the necessary
        models when dotted notation is used. Inner implies non dotted columns
        and many to one and one to one

        :param query:
        :param select_columns:
        :return:
        """
        if not select_columns:
            return query

        joined_models = []
        for column in select_columns:
            if not is_column_dotted(column):
                query = self._apply_normal_col_select_option(query, column)
                continue

            # Dotted column
            root_relation = get_column_root_relation(column)
            leaf_column = get_column_leaf(column)
            related_model = self.get_alias_mapping(root_relation, aliases_mapping)
            relation = getattr(self.obj, root_relation)

            if self.is_relation_many_to_one(
                root_relation
            ) or self.is_relation_many_to_many_special(root_relation):
                if root_relation not in joined_models:
                    query = self._query_join_relation(
                        query, root_relation, aliases_mapping=aliases_mapping
                    )
                    query = query.add_entity(
                        self.get_alias_mapping(root_relation, aliases_mapping)
                    )
                    # Add relation FK to avoid N+1 performance issue
                    query = self._apply_relation_fks_select_options(
                        query, root_relation
                    )
                    joined_models.append(root_relation)

                related_model = self.get_alias_mapping(root_relation, aliases_mapping)
                relation = getattr(self.obj, root_relation)
                # The Zen of eager loading :(
                # https://docs.sqlalchemy.org/en/13/orm/loading_relationships.html
                query = query.options(
                    contains_eager(relation.of_type(related_model)).load_only(
                        leaf_column
                    )
                )
                query = query.options(Load(related_model).load_only(leaf_column))
        return query

    def apply_outer_select_joins(
        self,
        query: Query,
        select_columns: List[str] = None,
        outer_default_load: bool = False,
    ) -> Query:
        if not select_columns:
            return query

        for column in select_columns:
            if not is_column_dotted(column):
                query = self._apply_normal_col_select_option(query, column)
                continue

            root_relation = get_column_root_relation(column)
            leaf_column = get_column_leaf(column)

            if self.is_relation_many_to_many(
                root_relation
            ) or self.is_relation_one_to_many(root_relation):
                if outer_default_load:
                    query = query.options(
                        Load(self.obj).defaultload(root_relation).load_only(leaf_column)
                    )
                else:
                    query = query.options(
                        Load(self.obj).joinedload(root_relation).load_only(leaf_column)
                    )
            else:
                related_model = self.get_related_model(root_relation)
                query = query.options(Load(related_model).load_only(leaf_column))

        return query

    def get_inner_filters(self, filters: Optional[Filters]) -> Filters:
        """
        Inner filters are non dotted columns and
        one to many or one to one relations

        :param filters: All filters
        :return: New filtered filters to apply to an inner query
        """
        inner_filters = Filters(self.filter_converter_class, self)
        _filters = []
        if filters:
            for flt, value in zip(filters.filters, filters.values):
                if not is_column_dotted(flt.column_name):
                    _filters.append((flt.column_name, flt.__class__, value))
                elif self.is_relation_many_to_one(
                    get_column_root_relation(flt.column_name)
                ) or self.is_relation_one_to_one(
                    get_column_root_relation(flt.column_name)
                ):
                    _filters.append((flt.column_name, flt.__class__, value))
            inner_filters.add_filter_list(_filters)
        return inner_filters

    def exists_col_to_many(self, select_columns: List[str]) -> bool:
        for column in select_columns:
            if is_column_dotted(column):
                root_relation = get_column_root_relation(column)
                if self.is_relation_many_to_many(
                    root_relation
                ) or self.is_relation_one_to_many(root_relation):
                    return True
        return False

    def get_alias_mapping(
        self, model_name: str, aliases_mapping: Dict[str, AliasedClass]
    ) -> Union[AliasedClass, Type[Model]]:
        if aliases_mapping is None:
            return self.get_related_model(model_name)
        return aliases_mapping.get(model_name, self.get_related_model(model_name))

    def _apply_inner_all(
        self,
        query: Query,
        filters: Optional[Filters] = None,
        order_column: str = "",
        order_direction: str = "",
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        select_columns: Optional[List[str]] = None,
        aliases_mapping: Dict[str, AliasedClass] = None,
    ) -> Query:
        inner_filters = self.get_inner_filters(filters)
        query = self.apply_inner_select_joins(query, select_columns, aliases_mapping)
        query = self.apply_filters(query, inner_filters)
        query = self.apply_engine_specific_hack(query, page, page_size, order_column)
        query = self.apply_order_by(
            query,
            order_column,
            order_direction,
            aliases_mapping=aliases_mapping,
            add_pk=True,
        )
        query = self.apply_pagination(query, page, page_size)
        return query

    def query_count(
        self,
        query: Query,
        filters: Optional[Filters] = None,
        select_columns: Optional[List[str]] = None,
    ) -> int:
        return self._apply_inner_all(
            query, filters, select_columns=select_columns, aliases_mapping={}
        ).count()

    def apply_all(
        self,
        query: Query,
        filters: Optional[Filters] = None,
        order_column: str = "",
        order_direction: str = "",
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        select_columns: Optional[List[str]] = None,
        outer_default_load: bool = False,
    ) -> Query:
        """
        Accepts a SQLAlchemy Query and applies all filtering logic, order by and
        pagination.

        :param query: The query to apply all
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
        :param select_columns:
            A List of columns to be specifically selected on the query
        :param outer_default_load: If True, the default load for outer joins will be
            applied. This is useful for when you want to control
            the load of the many-to-many relationships at the model level.
            we will apply:
             https://docs.sqlalchemy.org/en/14/orm/loading_relationships.html#sqlalchemy.orm.Load.defaultload
        :return: A SQLAlchemy Query with all the applied logic
        """
        aliases_mapping = {}
        inner_query = self._apply_inner_all(
            query,
            filters,
            order_column,
            order_direction,
            page,
            page_size,
            select_columns,
            aliases_mapping=aliases_mapping,
        )
        # Only use a from_self if we need to select a join one to many or many to many
        if select_columns and self.exists_col_to_many(select_columns):
            if select_columns and order_column:
                select_columns = select_columns + [order_column]
            outer_query = inner_query.from_self()
            outer_query = self.apply_outer_select_joins(
                outer_query,
                select_columns,
                outer_default_load=outer_default_load,
            )
            return self.apply_order_by(outer_query, order_column, order_direction)
        else:
            return inner_query

    def query(
        self,
        filters: Optional[Filters] = None,
        order_column: str = "",
        order_direction: str = "",
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        select_columns: Optional[List[str]] = None,
        outer_default_load: bool = False,
    ) -> Tuple[int, List[Model]]:
        """
        Returns the results for a model query, applies filters, sorting and pagination

        :param filters: A Filter class that contains all filters to apply
        :param order_column: name of the column to order
        :param order_direction: the direction to order <'asc'|'desc'>
        :param page: the current page
        :param page_size: the current page size
        :param select_columns: A List of columns to be specifically selected
        on the query. Supports dotted notation.
        :param outer_default_load: If True, the default load for outer joins will be
            applied. This is useful for when you want to control
            the load of the many-to-many relationships at the model level.
            we will apply:
             https://docs.sqlalchemy.org/en/14/orm/loading_relationships.html#sqlalchemy.orm.Load.defaultload
        :return: A tuple with the query count (non paginated) and the results
        """
        if not self.session:
            raise InterfaceQueryWithoutSession()
        query = self.session.query(self.obj)

        count = self.query_count(query, filters, select_columns)
        query = self.apply_all(
            query,
            filters,
            order_column,
            order_direction,
            page,
            page_size,
            select_columns,
        )
        query_results = query.all()

        result = []
        for item in query_results:
            if hasattr(item, self.obj.__name__):
                result.append(getattr(item, self.obj.__name__))
            else:
                return count, query_results
        return count, result

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

    def is_image(self, col_name: str) -> bool:
        try:
            return isinstance(self.list_columns[col_name].type, ImageColumn)
        except KeyError:
            return False

    def is_file(self, col_name: str) -> bool:
        try:
            return isinstance(self.list_columns[col_name].type, FileColumn)
        except KeyError:
            return False

    def is_string(self, col_name: str) -> bool:
        try:
            return (
                _is_sqla_type(self.list_columns[col_name].type, sa_types.String)
                or self.list_columns[col_name].type.__class__ == UUIDType
            )
        except KeyError:
            return False

    def is_text(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.Text)
        except KeyError:
            return False

    def is_binary(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.LargeBinary)
        except KeyError:
            return False

    def is_integer(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.Integer)
        except KeyError:
            return False

    def is_numeric(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.Numeric)
        except KeyError:
            return False

    def is_float(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.Float)
        except KeyError:
            return False

    def is_boolean(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.Boolean)
        except KeyError:
            return False

    def is_date(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.Date)
        except KeyError:
            return False

    def is_datetime(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.DateTime)
        except KeyError:
            return False

    def is_enum(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.Enum)
        except KeyError:
            return False

    def is_relation(self, col_name: str) -> bool:
        try:
            return isinstance(self.list_properties[col_name], RelationshipProperty)
        except KeyError:
            return False

    def is_relation_many_to_one(self, col_name: str) -> bool:
        try:
            if self.is_relation(col_name):
                return self.list_properties[col_name].direction.name == "MANYTOONE"
            return False
        except KeyError:
            return False

    def is_relation_many_to_many(self, col_name: str) -> bool:
        try:
            if self.is_relation(col_name):
                relation = self.list_properties[col_name]
                return relation.direction.name == "MANYTOMANY"
            return False
        except KeyError:
            return False

    def is_relation_many_to_many_special(self, col_name: str) -> bool:
        try:
            if self.is_relation(col_name):
                relation = self.list_properties[col_name]
                return relation.direction.name == "ONETOONE" and relation.uselist
            return False
        except KeyError:
            return False

    def is_relation_one_to_one(self, col_name: str) -> bool:
        try:
            if self.is_relation(col_name):
                relation = self.list_properties[col_name]
                return self.list_properties[col_name].direction.name == "ONETOONE" or (
                    relation.direction.name == "ONETOMANY" and relation.uselist is False
                )
            return False
        except KeyError:
            return False

    def is_relation_one_to_many(self, col_name: str) -> bool:
        try:
            if self.is_relation(col_name):
                relation = self.list_properties[col_name]
                return relation.direction.name == "ONETOMANY" and relation.uselist
            return False
        except KeyError:
            return False

    def is_nullable(self, col_name: str) -> bool:
        if self.is_relation_many_to_one(col_name):
            col = self.get_relation_fk(col_name)
            return col.nullable
        try:
            return self.list_columns[col_name].nullable
        except KeyError:
            return False

    def is_unique(self, col_name: str) -> bool:
        try:
            return self.list_columns[col_name].unique is True
        except KeyError:
            return False

    def is_pk(self, col_name: str) -> bool:
        try:
            return self.list_columns[col_name].primary_key
        except KeyError:
            return False

    def is_pk_composite(self) -> bool:
        return len(self.obj.__mapper__.primary_key) > 1

    def is_fk(self, col_name: str) -> bool:
        try:
            return self.list_columns[col_name].foreign_keys
        except KeyError:
            return False

    def is_property(self, col_name: str) -> bool:
        return hasattr(getattr(self.obj, col_name), "fget")

    def is_function(self, col_name: str) -> bool:
        return hasattr(getattr(self.obj, col_name), "__call__")

    def is_property_or_function(self, col_name: str) -> bool:
        return self.is_property(col_name) or self.is_function(col_name)

    def get_max_length(self, col_name: str) -> int:
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

    def add(self, item: Model, raise_exception: bool = False) -> bool:
        try:
            self.session.add(item)
            self.session.commit()
            self.message = (as_unicode(self.add_row_message), "success")
            return True
        except IntegrityError as e:
            self.message = (as_unicode(self.add_integrity_error_message), "warning")
            log.warning(LOGMSG_WAR_DBI_ADD_INTEGRITY, e)
            self.session.rollback()
            if raise_exception:
                raise e
            return False
        except Exception as e:
            self.message = (as_unicode(self.database_error_message), "danger")
            log.exception("Database error")
            self.session.rollback()
            if raise_exception:
                raise e
            return False

    def edit(self, item: Model, raise_exception: bool = False) -> bool:
        try:
            self.session.merge(item)
            self.session.commit()
            self.message = (as_unicode(self.edit_row_message), "success")
            return True
        except IntegrityError as e:
            self.message = (as_unicode(self.edit_integrity_error_message), "warning")
            log.warning(LOGMSG_WAR_DBI_EDIT_INTEGRITY, e)
            self.session.rollback()
            if raise_exception:
                raise e
            return False
        except Exception as e:
            self.message = (as_unicode(self.database_error_message), "danger")
            log.exception("Database error")
            self.session.rollback()
            if raise_exception:
                raise e
            return False

    def delete(self, item: Model, raise_exception: bool = False) -> bool:
        try:
            self._delete_files(item)
            self.session.delete(item)
            self.session.commit()
            self.message = (as_unicode(self.delete_row_message), "success")
            return True
        except IntegrityError as e:
            self.message = (as_unicode(self.delete_integrity_error_message), "warning")
            log.warning(LOGMSG_WAR_DBI_DEL_INTEGRITY, e)
            self.session.rollback()
            if raise_exception:
                raise e
            return False
        except Exception as e:
            self.message = (as_unicode(self.database_error_message), "danger")
            log.exception("Database error")
            self.session.rollback()
            if raise_exception:
                raise e
            return False

    def delete_all(self, items: List[Model]) -> bool:
        try:
            for item in items:
                self._delete_files(item)
                self.session.delete(item)
            self.session.commit()
            self.message = (as_unicode(self.delete_row_message), "success")
            return True
        except IntegrityError as e:
            self.message = (as_unicode(self.delete_integrity_error_message), "warning")
            log.warning(LOGMSG_WAR_DBI_DEL_INTEGRITY, e)
            self.session.rollback()
            return False
        except Exception as e:
            self.message = (as_unicode(self.database_error_message), "danger")
            log.exception(LOGMSG_ERR_DBI_DEL_GENERIC, e)
            self.session.rollback()
            return False

    """
    -----------------------
     FILE HANDLING METHODS
    -----------------------
    """

    def _add_files(self, this_request, item: Model):
        fm = FileManager()
        im = ImageManager()
        for file_col in this_request.files:
            if self.is_file(file_col):
                fm.save_file(this_request.files[file_col], getattr(item, file_col))
        for file_col in this_request.files:
            if self.is_image(file_col):
                im.save_file(this_request.files[file_col], getattr(item, file_col))

    def _delete_files(self, item: Model):
        for file_col in self.get_file_column_list():
            if self.is_file(file_col) and getattr(item, file_col):
                fm = FileManager()
                fm.delete_file(getattr(item, file_col))
        for file_col in self.get_image_column_list():
            if self.is_image(file_col) and getattr(item, file_col):
                im = ImageManager()
                im.delete_file(getattr(item, file_col))

    """
    ------------------------------
     FUNCTIONS FOR RELATED MODELS
    ------------------------------
    """

    def get_col_default(self, col_name: str) -> Any:
        default = getattr(self.list_columns[col_name], "default", None)
        if default is None:
            return None

        value = getattr(default, "arg", None)
        if value is None:
            return None

        if getattr(default, "is_callable", False):
            return lambda: default.arg(None)

        if not getattr(default, "is_scalar", True):
            return None

        return value

    def get_related_model(self, col_name: str) -> Type[Model]:
        return self.list_properties[col_name].mapper.class_

    def get_related_model_and_join(
        self, col_name: str
    ) -> List[Tuple[Type[Model], object]]:
        relation = self.list_properties[col_name]
        if relation.direction.name == "MANYTOMANY":
            return [
                (relation.secondary, relation.primaryjoin),
                (relation.mapper.class_, relation.secondaryjoin),
            ]
        return [(relation.mapper.class_, relation.primaryjoin)]

    def get_related_interface(self, col_name: str):
        return self.__class__(self.get_related_model(col_name), self.session)

    def get_related_obj(self, col_name: str, value: Any) -> Optional[Type[Model]]:
        rel_model = self.get_related_model(col_name)
        if self.session:
            return self.session.query(rel_model).get(value)
        return None

    def get_related_fks(self, related_views) -> List[str]:
        return [view.datamodel.get_related_fk(self.obj) for view in related_views]

    def get_related_fk(self, model: Type[Model]) -> Optional[str]:
        for col_name in self.list_properties.keys():
            if self.is_relation(col_name):
                if model == self.get_related_model(col_name):
                    return col_name
        return None

    def get_info(self, col_name: str):
        if col_name in self.list_properties:
            return self.list_properties[col_name].info
        return {}

    """
    -------------
     GET METHODS
    -------------
    """

    def get_columns_list(self) -> List[str]:
        """
        Returns all model's columns on SQLA properties
        """
        return list(self.list_properties.keys())

    def get_user_columns_list(self) -> List[str]:
        """
        Returns all model's columns except pk or fk
        """
        return [
            col_name
            for col_name in self.get_columns_list()
            if (not self.is_pk(col_name)) and (not self.is_fk(col_name))
        ]

    # TODO get different solution, more integrated with filters
    def get_search_columns_list(self) -> List[str]:
        ret_lst = []
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

    def get_order_columns_list(self, list_columns: List[str] = None) -> List[str]:
        """
        Returns the columns that can be ordered.

        :param list_columns: optional list of columns name, if provided will
            use this list only.
        """
        ret_lst = []
        list_columns = list_columns or self.get_columns_list()

        for col_name in list_columns:
            if self.is_relation(col_name):
                continue

            if hasattr(self.obj, col_name):
                attribute = getattr(self.obj, col_name)
                if not callable(attribute) or hasattr(attribute, "_col_name"):
                    ret_lst.append(col_name)
            else:
                ret_lst.append(col_name)

        return ret_lst

    def get_file_column_list(self) -> List[str]:
        return [
            i.name
            for i in self.obj.__mapper__.columns
            if isinstance(i.type, FileColumn)
        ]

    def get_image_column_list(self) -> List[str]:
        return [
            i.name
            for i in self.obj.__mapper__.columns
            if isinstance(i.type, ImageColumn)
        ]

    def get_property_first_col(self, col_name: str) -> ColumnProperty:
        # support for only one col for pk and fk
        return self.list_properties[col_name].columns[0]

    def get_relation_fk(self, col_name: str) -> str:
        # support for only one col for pk and fk
        return list(self.list_properties[col_name].local_columns)[0]

    def get(
        self,
        id,
        filters: Optional[Filters] = None,
        select_columns: Optional[List[str]] = None,
        outer_default_load: bool = False,
    ) -> Optional[Model]:
        """
        Returns the result for a model get, applies filters and supports dotted
        notation for joins and granular selecting query columns.

        :param id: The model id (pk).
        :param filters: A Filter class that contains all filters to apply.
        :param select_columns: A List of columns to be specifically selected.
        on the query. Supports dotted notation.
        :return:
        """
        pk = self.get_pk_name()
        if filters:
            _filters = filters.copy()
        else:
            _filters = Filters(self.filter_converter_class, self)

        if self.is_pk_composite():
            for _pk, _id in zip(pk, id):
                _filters.add_filter(_pk, self.FilterEqual, _id)
        else:
            _filters.add_filter(pk, self.FilterEqual, id)
        query = self.session.query(self.obj)
        item = self.apply_all(
            query,
            _filters,
            select_columns=select_columns,
            outer_default_load=outer_default_load,
        ).one_or_none()
        if item:
            if hasattr(item, self.obj.__name__):
                return getattr(item, self.obj.__name__)
        return item

    def get_pk_name(self) -> Optional[Union[List[str], str]]:
        """
        Get the model primary key column name.
        """
        return self._get_pk_name(self.obj)

    def get_pk(self, model: Optional[Type[Model]] = None):
        """
        Get the model primary key SQLAlchemy column.
        Will not support composite keys
        """
        model_ = model or self.obj
        pk_name = self._get_pk_name(model_)
        if pk_name and isinstance(pk_name, str):
            return getattr(model_, pk_name)
        return None

    def _get_pk_name(self, model: Type[Model]) -> Optional[Union[List[str], str]]:
        pk = [pk.name for pk in model.__mapper__.primary_key]
        if pk:
            return pk if self.is_pk_composite() else pk[0]
        return None


def _include_filters(interface: SQLAInterface) -> None:
    """
    Injects all filters on the interface class itself
    :param interface:
    """
    for key in filters.__all__:
        if not hasattr(interface, key):
            setattr(interface, key, getattr(filters, key))


"""
    For Retro-Compatibility
"""
SQLModel = SQLAInterface
