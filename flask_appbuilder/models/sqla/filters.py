import logging
from flask.ext.babelpkg import lazy_gettext
from ..filters import BaseFilter, FilterRelation, BaseFilterConverter

log = logging.getLogger(__name__)


__all__ = ['SQLAFilterConverter', 'FilterEqual', 'FilterNotStartsWith', 'FilterStartsWith', 'FilterContains',
           'FilterNotEqual', 'FilterEndsWith', 'FilterEqualFunction', 'FilterGreater', 'FilterNotEndsWith',
           'FilterRelationManyToManyEqual', 'FilterRelationOneToManyEqual', 'FilterRelationOneToManyNotEqual',
           'FilterSmaller', 'FilterYes', 'FilterNo', 'FilterBefore', 'FilterAfter']

def get_field_setup_query(query, model, column_name):
    """
        Help function for SQLA filters, checks for dot notation on column names.
        If it exists, will join the query with the model from the first part of the field name.

        example:
            Contact.created_by: if created_by is a User model, it will be joined to the query.
    """
    if not hasattr(model, column_name):
       # it's an inner obj attr
        rel_model = getattr(model, column_name.split('.')[0]).mapper.class_
        query = query.join(rel_model)
        return query, getattr(rel_model, column_name.split('.')[1])
    else:
        return query, getattr(model, column_name)

class FilterStartsWith(BaseFilter):
    name = lazy_gettext('Begins with')

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field.like(value + '%'))


class FilterNotStartsWith(BaseFilter):
    name = lazy_gettext('Does not begin with')

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(~field.like(value + '%'))


class FilterEndsWith(BaseFilter):
    name = lazy_gettext('Ends with')

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field.like('%' + value))


class FilterNotEndsWith(BaseFilter):
    name = lazy_gettext('Does not end with')

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(~field.like('%' + value))


class FilterContains(BaseFilter):
    name = lazy_gettext('Contains')

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field.like('%' + value + '%'))


class FilterNotContains(BaseFilter):
    name = lazy_gettext('Does not contain')

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(~field.like('%' + value + '%'))


class FilterEqual(BaseFilter):
    name = lazy_gettext('Equal to')

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        if self.datamodel.is_boolean(self.column_name):
            if value == 'y':
                value = True
        return query.filter(field == value)


class FilterNotEqual(BaseFilter):
    name = lazy_gettext('Not equal to')

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        if self.datamodel.is_boolean(self.column_name):
            if value == 'y':
                value = True
        return query.filter(field != value)


class FilterYes(BaseFilter):
    name = lazy_gettext('Yes')

    def apply(self, query, value):
        if self.datamodel.is_boolean(self.column_name):
            if value == 'y':
                value = True
        return query.filter(getattr(self.model, self.column_name) == value)


class FilterNo(BaseFilter):
    name = lazy_gettext('No')

    def apply(self, query, value):
        if self.datamodel.is_boolean(self.column_name):
            if value == 'n':
                value = False
        return query.filter(getattr(self.model, self.column_name) == value)


class FilterGreater(BaseFilter):
    name = lazy_gettext('Greater than')

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field > value)


class FilterSmaller(BaseFilter):
    name = lazy_gettext('Less than')

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field < value)


class FilterAfter(BaseFilter):
    name = lazy_gettext('After')

    def apply(self, query, value):
        return query.filter(getattr(self.model, self.column_name) > value)


class FilterBefore(BaseFilter):
    name = lazy_gettext('Before')

    def apply(self, query, value):
        return query.filter(getattr(self.model, self.column_name) < value)

class FilterRelationOneToManyEqual(FilterRelation):
    name = lazy_gettext('Is')

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        rel_obj = self.datamodel.get_related_obj(self.column_name, value)
        return query.filter(field == rel_obj)


class FilterRelationOneToManyNotEqual(FilterRelation):
    name = lazy_gettext('Is not')

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        rel_obj = self.datamodel.get_related_obj(self.column_name, value)
        return query.filter(field != rel_obj)


class FilterRelationManyToManyEqual(FilterRelation):
    name = lazy_gettext('Relation as many')

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        rel_obj = self.datamodel.get_related_obj(self.column_name, value)
        return query.filter(field.contains(rel_obj))


class FilterEqualFunction(BaseFilter):
    name = "Filter view with a function"

    def apply(self, query, func):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field == func())


class SQLAFilterConverter(BaseFilterConverter):
    """
        Class for converting columns into a supported list of filters
        specific for SQLAlchemy.

    """
    conversion_table = (('is_relation_many_to_one', [FilterRelationOneToManyEqual,
                        FilterRelationOneToManyNotEqual]),
                        ('is_relation_one_to_one', [FilterRelationOneToManyEqual,
                        FilterRelationOneToManyNotEqual]),
                        ('is_relation_many_to_many', [FilterRelationManyToManyEqual]),
                        ('is_relation_one_to_many', [FilterRelationManyToManyEqual]),
                        ('is_text', [FilterStartsWith,
                                     FilterEndsWith,
                                     FilterContains,
                                     FilterEqual,
                                     FilterNotStartsWith,
                                     FilterNotEndsWith,
                                     FilterNotContains,
                                     FilterNotEqual]),
                        ('is_string', [FilterStartsWith,
                                       FilterEndsWith,
                                       FilterContains,
                                       FilterEqual,
                                       FilterNotStartsWith,
                                       FilterNotEndsWith,
                                       FilterNotContains,
                                       FilterNotEqual]),
                        ('is_integer', [FilterEqual,
                                        FilterGreater,
                                        FilterSmaller,
                                        FilterNotEqual]),
                        ('is_float', [FilterEqual,
                                      FilterGreater,
                                      FilterSmaller,
                                      FilterNotEqual]),
                        ('is_numeric', [FilterEqual,
                                      FilterGreater,
                                      FilterSmaller,
                                      FilterNotEqual]),
                        ('is_date', [FilterEqual,
                                     FilterAfter,
                                     FilterBefore,
                                     FilterNotEqual]),
                        ('is_boolean', [FilterYes,
                                     FilterNo]),
                        ('is_datetime', [FilterEqual,
                                         FilterAfter,
                                         FilterBefore,
                                         FilterNotEqual]),
    )
