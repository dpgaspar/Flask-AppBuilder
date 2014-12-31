import logging
from flask.ext.babelpkg import lazy_gettext
from ..filters import BaseFilter, FilterRelation, BaseFilterConverter

log = logging.getLogger(__name__)


class FilterEqual(BaseFilter):
    name = lazy_gettext('Equal to')

    def apply(self, query, value):
        if self.datamodel.is_boolean(self.column_name):
            if value == 'y':
                value = True
        return query.filter(getattr(self.model, self.column_name) == value)


class MongoEngineFilterConverter(BaseFilterConverter):
    """
        Class for converting columns into a supported list of filters
        specific for SQLAlchemy.

    """
    conversion_table = (('is_string', [FilterEqual]),)
