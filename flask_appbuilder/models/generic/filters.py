from flask.ext.babelpkg import lazy_gettext
from ..base import BaseFilter, FilterRelation, BaseFilterConverter


class FilterContains(BaseFilter):
    name = lazy_gettext('Starts with')

    def apply(self, query, value):
        return query.like(self.column_name, value)

class FilterEqual(BaseFilter):
    name = lazy_gettext('Equal to')

    def apply(self, query, value):
        return query.equal(self.column_name, value)



class VolFilterConverter(BaseFilterConverter):
    """
        Class for converting columns into a supported list of filters
        specific for SQLAlchemy.

    """
    conversion_table = (('is_text', [FilterContains,
                                     FilterEqual]
                                     ),
                        ('is_string', [FilterContains,
                                       FilterEqual]),
                        )

