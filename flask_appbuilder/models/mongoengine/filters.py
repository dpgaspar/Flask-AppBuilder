import logging
from flask.ext.babelpkg import lazy_gettext
from ..filters import BaseFilter, FilterRelation, BaseFilterConverter

log = logging.getLogger(__name__)


class FilterEqual(BaseFilter):
    name = lazy_gettext('Equal to')

    def apply(self, query, value):
        flt = {'%s' % self.column_name: value}
        return query.filter(**flt)


class FilterStartsWith(BaseFilter):
    name = lazy_gettext('Starts with')

    def apply(self, query, value):
        flt = {'%s__%s' % (self.column_name, 'startswith'): value}
        return query.filter(**flt)


class FilterNotStartsWith(BaseFilter):
    name = lazy_gettext('Not Starts with')

    def apply(self, query, value):
        flt = {'%s__not__%s' % (self.column_name, 'startswith'): value}
        return query.filter(**flt)


class FilterContains(BaseFilter):
    name = lazy_gettext('Contains')

    def apply(self, query, value):
        flt = {'%s__%s' % (self.column_name, 'icontains'): value}
        return query.filter(**flt)


class FilterNotContains(BaseFilter):
    name = lazy_gettext('Not Contains')

    def apply(self, query, value):
        flt = {'%s__not__%s' % (self.column_name, 'icontains'): value}
        return query.filter(**flt)


class MongoEngineFilterConverter(BaseFilterConverter):
    """
        Class for converting columns into a supported list of filters
        specific for SQLAlchemy.

    """
    conversion_table = (('is_string', [FilterEqual,
                                       FilterStartsWith,
                                       FilterNotStartsWith,
                                       FilterContains,
                                       FilterNotContains]),)
