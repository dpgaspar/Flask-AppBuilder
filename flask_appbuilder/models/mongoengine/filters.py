from ..base import BaseFilter, FilterRelation, BaseFilterConverter


class MongoEngineFilterConverter(BaseFilterConverter):
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
