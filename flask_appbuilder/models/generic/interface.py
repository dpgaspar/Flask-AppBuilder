from filters import VolFilterConverter
from ..base import BaseInterface
from ..filters import Filters


class VolInterface(BaseInterface):

    def __init__(self, obj, session=None):
        self.session = session
        super(VolInterface, self).__init__(obj)


    def get_filters(self, search_columns=[]):
        return Filters(VolFilterConverter, search_columns, self)


    def query(self, filters=None, order_column='', order_direction='',
              page=None, page_size=None):

        query = self.session.query()
        if filters:
            query = filters.apply_all(query)
        if order_column != '':
            query = query.order_by(order_column + ' ' + order_direction)
        result = query.all()
        return len(result), result

    def is_string(self, col_name):
        return True

    def is_nullable(self, col_name):
        return True

    def is_unique(self, col_name):
        return False

    def get_columns_list(self):
        return self.obj.columns

    def get_search_columns_list(self):
        return self.obj.columns

    def get_order_columns_list(self):
        return self.obj.columns


