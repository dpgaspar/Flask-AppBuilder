from .filters import MongoEngineFilterConverter
from ..base import BaseInterface
from ..filters import Filters
from mongoengine.fields import StringField, IntField

class MongoEngineInterface(BaseInterface):

    def __init__(self, obj, session=None):
        self.session = session
        super(MongoEngineInterface, self).__init__(obj)

    def get_filters(self, search_columns=[]):
        return Filters(MongoEngineFilterConverter, search_columns, self)

    def query(self, filters=None, order_column='', order_direction='',
              page=None, page_size=None):
        pass

    def is_string(self, col_name):
        return isinstance(self.obj._fields[col_name], StringField)

    def is_integer(self, col_name):
        return isinstance(self.obj._fields[col_name], IntField)

    def is_nullable(self, col_name):
        return self.obj.properties[col_name].nullable

    def is_unique(self, col_name):
        return self.obj.properties[col_name].unique

    def is_pk(self, col_name):
        return self.obj.properties[col_name].primary_key

    def get_columns_list(self):
        return self.obj._fields.keys()

    def get_search_columns_list(self):
        return self.obj._fields.keys()

    def get_order_columns_list(self, list_columns=None):
        return self.obj._fields.keys()

    def get_keys(self, lst):
        """
            return a list of pk values from object list
        """
        pk_name = self.get_pk_name()
        return [getattr(item, pk_name) for item in lst]

    def get_pk_name(self):
        return 'id'

    def get(self, id):
        return self.obj.objects(pk=id)
