import datetime
import logging

from dateutil import parser
from flask_appbuilder.exceptions import ApplyFilterException
from flask_appbuilder.models.filters import (
    BaseFilter,
    BaseFilterConverter,
    FilterRelation,
)
from flask_babel import lazy_gettext
from sqlalchemy.exc import SQLAlchemyError

log = logging.getLogger(__name__)


__all__ = [
    "SQLAFilterConverter",
    "FilterEqual",
    "FilterNotStartsWith",
    "FilterStartsWith",
    "FilterContains",
    "FilterNotContains",
    "FilterNotEqual",
    "FilterEndsWith",
    "FilterEqualFunction",
    "FilterGreater",
    "FilterNotEndsWith",
    "FilterIn",
    "FilterNotIn",
    "FilterRelationManyToManyEqual",
    "FilterRelationOneToManyEqual",
    "FilterRelationOneToManyNotEqual",
    "FilterSmaller",
]


def get_field_setup_query(query, model, column_name):
    """
    Help function for SQLA filters, checks for dot notation on column names.
    If it exists, will join the query with the model
    from the first part of the field name.

    example:
        Contact.created_by: if created_by is a User model,
        it will be joined to the query.
    """
    if not hasattr(model, column_name):
        # it's an inner obj attr
        rel_model = getattr(model, column_name.split(".")[0]).mapper.class_
        query = query.join(rel_model)
        return query, getattr(rel_model, column_name.split(".")[1])
    else:
        return query, getattr(model, column_name)


def set_value_to_type(datamodel, column_name, value):
    if datamodel.is_integer(column_name):
        try:
            return int(value)
        except Exception:
            return None
    elif datamodel.is_float(column_name):
        try:
            return float(value)
        except Exception:
            return None
    elif datamodel.is_boolean(column_name):
        if value == "y":
            return True
    elif datamodel.is_date(column_name) and not isinstance(value, datetime.date):
        try:
            return parser.parse(value).date()
        except Exception:
            return None
    elif datamodel.is_datetime(column_name) and not isinstance(
        value, datetime.datetime
    ):
        try:
            return parser.parse(value)
        except Exception:
            return None
    elif datamodel.is_json(column_name):
        # For JSON columns, treat as string for filtering
        return str(value)
    return value


class FilterStartsWith(BaseFilter):
    name = lazy_gettext("Starts with")
    arg_name = "sw"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field.ilike(value + "%"))


class FilterNotStartsWith(BaseFilter):
    name = lazy_gettext("Not Starts with")
    arg_name = "nsw"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(~field.ilike(value + "%"))


class FilterEndsWith(BaseFilter):
    name = lazy_gettext("Ends with")
    arg_name = "ew"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field.ilike("%" + value))


class FilterNotEndsWith(BaseFilter):
    name = lazy_gettext("Not Ends with")
    arg_name = "new"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(~field.ilike("%" + value))


class FilterContains(BaseFilter):
    name = lazy_gettext("Contains")
    arg_name = "ct"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field.ilike("%" + value + "%"))


class FilterNotContains(BaseFilter):
    name = lazy_gettext("Not Contains")
    arg_name = "nct"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(~field.ilike("%" + value + "%"))


class FilterEqual(BaseFilter):
    name = lazy_gettext("Equal to")
    arg_name = "eq"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        value = set_value_to_type(self.datamodel, self.column_name, value)
        return query.filter(field == value)


class FilterNotEqual(BaseFilter):
    name = lazy_gettext("Not Equal to")
    arg_name = "neq"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        value = set_value_to_type(self.datamodel, self.column_name, value)

        return query.filter(field != value)


class FilterGreater(BaseFilter):
    name = lazy_gettext("Greater than")
    arg_name = "gt"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        value = set_value_to_type(self.datamodel, self.column_name, value)

        if value is None:
            return query

        return query.filter(field > value)


class FilterSmaller(BaseFilter):
    name = lazy_gettext("Smaller than")
    arg_name = "lt"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        value = set_value_to_type(self.datamodel, self.column_name, value)

        if value is None:
            return query

        return query.filter(field < value)


class FilterIn(BaseFilter):
    name = lazy_gettext("In")
    arg_name = "in"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        typed_values = [
            set_value_to_type(self.datamodel, self.column_name, v) for v in value
        ]
        return query.filter(field.in_(typed_values))


class FilterNotIn(BaseFilter):
    name = lazy_gettext("Not In")
    arg_name = "not_in"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        typed_values = [
            set_value_to_type(self.datamodel, self.column_name, v) for v in value
        ]
        return query.filter(~field.in_(typed_values))


class FilterRelationOneToManyEqual(FilterRelation):
    name = lazy_gettext("Relation")
    arg_name = "rel_o_m"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        try:
            rel_obj = self.datamodel.get_related_obj(self.column_name, value)
        except SQLAlchemyError as exc:
            logging.warning(
                "Filter exception for %s with value %s, will not apply", field, value
            )
            try:
                self.datamodel.session.rollback()
            except SQLAlchemyError:
                # on MSSQL a rollback would fail here
                pass
            raise ApplyFilterException(exception=exc)
        return query.filter(field == rel_obj)


class FilterRelationOneToManyNotEqual(FilterRelation):
    name = lazy_gettext("No Relation")
    arg_name = "nrel_o_m"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        try:
            rel_obj = self.datamodel.get_related_obj(self.column_name, value)
        except SQLAlchemyError as exc:
            logging.warning(
                "Filter exception for %s with value %s, will not apply", field, value
            )
            try:
                self.datamodel.session.rollback()
            except SQLAlchemyError:
                # on MSSQL a rollback would fail here
                pass
            raise ApplyFilterException(exception=exc)
        return query.filter(field != rel_obj)


class FilterRelationManyToManyEqual(FilterRelation):
    name = lazy_gettext("Relation as Many")
    arg_name = "rel_m_m"

    def apply_item(self, query, field, value_item):
        """
        Get object by column_name and value_item, then apply filter if object exists
        Query with new filter applied
        """
        try:
            rel_obj = self.datamodel.get_related_obj(self.column_name, value_item)
        except SQLAlchemyError as exc:
            logging.warning(
                "Filter exception for %s with value %s, will not apply",
                field,
                value_item,
            )
            try:
                self.datamodel.session.rollback()
            except SQLAlchemyError:
                # on MSSQL a rollback would fail here
                pass
            raise ApplyFilterException(exception=exc)

        if rel_obj:
            return query.filter(field.contains(rel_obj))
        else:
            log.error(
                "Related object for column: %s, value: %s return Null",
                self.column_name,
                value_item,
            )

        return query

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)

        if isinstance(value, list):
            for value_item in value:
                query = self.apply_item(query, field, value_item)
            return query

        return self.apply_item(query, field, value)


class FilterEqualFunction(BaseFilter):
    name = "Filter view with a function"
    arg_name = "eqf"

    def apply(self, query, func):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field == func())


class FilterInFunction(BaseFilter):
    name = "Filter view where field is in a list returned by a function"
    arg_name = "inf"

    def apply(self, query, func):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field.in_(func()))


class SQLAFilterConverter(BaseFilterConverter):
    """
    Class for converting columns into a supported list of filters
    specific for SQLAlchemy.

    """

    conversion_table = (
        (
            "is_relation_many_to_one",
            [FilterRelationOneToManyEqual, FilterRelationOneToManyNotEqual],
        ),
        (
            "is_relation_one_to_one",
            [FilterRelationOneToManyEqual, FilterRelationOneToManyNotEqual],
        ),
        ("is_relation_many_to_many", [FilterRelationManyToManyEqual]),
        ("is_relation_one_to_many", [FilterRelationManyToManyEqual]),
        ("is_enum", [FilterEqual, FilterNotEqual]),
        (
            "is_text",
            [
                FilterStartsWith,
                FilterEndsWith,
                FilterContains,
                FilterEqual,
                FilterNotStartsWith,
                FilterNotEndsWith,
                FilterNotContains,
                FilterNotEqual,
                FilterIn,
                FilterNotIn,
            ],
        ),
        (
            "is_binary",
            [
                FilterStartsWith,
                FilterEndsWith,
                FilterContains,
                FilterEqual,
                FilterNotStartsWith,
                FilterNotEndsWith,
                FilterNotContains,
                FilterNotEqual,
            ],
        ),
        (
            "is_string",
            [
                FilterStartsWith,
                FilterEndsWith,
                FilterContains,
                FilterEqual,
                FilterNotStartsWith,
                FilterNotEndsWith,
                FilterNotContains,
                FilterNotEqual,
                FilterIn,
                FilterNotIn,
            ],
        ),
        (
            "is_integer",
            [
                FilterEqual,
                FilterGreater,
                FilterSmaller,
                FilterNotEqual,
                FilterIn,
                FilterNotIn,
            ],
        ),
        (
            "is_float",
            [
                FilterEqual,
                FilterGreater,
                FilterSmaller,
                FilterNotEqual,
                FilterIn,
                FilterNotIn,
            ],
        ),
        (
            "is_numeric",
            [
                FilterEqual,
                FilterGreater,
                FilterSmaller,
                FilterNotEqual,
                FilterIn,
                FilterNotIn,
            ],
        ),
        ("is_date", [FilterEqual, FilterGreater, FilterSmaller, FilterNotEqual]),
        ("is_boolean", [FilterEqual, FilterNotEqual]),
        ("is_datetime", [FilterEqual, FilterGreater, FilterSmaller, FilterNotEqual]),
        (
            "is_json",
            [
                FilterStartsWith,
                FilterEndsWith,
                FilterContains,
                FilterEqual,
                FilterNotStartsWith,
                FilterNotEndsWith,
                FilterNotContains,
                FilterNotEqual,
            ],
        ),
    )
