from flask.ext.babelpkg import lazy_gettext
from ..base import BaseFilter, FilterRelation, BaseFilterConverter


class FilterContains(BaseFilter):
    name = lazy_gettext('Contains')

    def apply(self, query, value):
        return query.like(self.column_name, value)

class FilterNotContains(BaseFilter):
    name = lazy_gettext('Not Contains')

    def apply(self, query, value):
        return query.not_like(self.column_name, value)


class FilterEqual(BaseFilter):
    name = lazy_gettext('Equal to')

    def apply(self, query, value):
        return query.equal(self.column_name, value)


class FilterNotEqual(BaseFilter):
    name = lazy_gettext('Not Equal to')

    def apply(self, query, value):
        return query.not_equal(self.column_name, value)




class GenericFilterConverter(BaseFilterConverter):
    """
        Class for converting columns into a supported list of filters
        specific for SQLAlchemy.

    """
    conversion_table = (('is_text', [FilterContains,
                                     FilterNotContains,
                                     FilterEqual,
                                     FilterNotEqual]
                                     ),
                        ('is_string', [FilterContains,
                                       FilterNotContains,
                                       FilterEqual,
                                       FilterNotEqual]),
                        ('is_integer', [FilterEqual,
                                        FilterNotEqual]),
                        )

