from flask.ext.babelpkg import lazy_gettext
from ..base import BaseFilter, FilterRelation


class FilterStartsWith(BaseFilter):
    name = lazy_gettext('Starts with')

    def apply(self, query, value):
        return query.like(self.column_name, value)
