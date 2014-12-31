import logging, sys
from flask import flash
from .filters import MongoEngineFilterConverter
from ..._compat import as_unicode
from ..base import BaseInterface
from ..filters import Filters
from mongoengine.fields import StringField, IntField

log = logging.getLogger(__name__)


class MongoEngineInterface(BaseInterface):

    filter_converter_class = MongoEngineFilterConverter

    def __init__(self, obj, session=None):
        self.session = session
        super(MongoEngineInterface, self).__init__(obj)

    def query(self, filters=None, order_column='', order_direction='',
              page=None, page_size=None):

        if filters:
            objs = filters.apply_all(self.obj.objects)
        else:
            objs = self.obj.objects
        count = len(objs)
        start, stop = 0, count
        if page:
            start = page * page_size
        if page_size:
            stop = start + page_size
        if order_column != '':
            if order_direction == 'asc':
                objs = objs.order_by('-{0}'.format(order_column))
            else:
                objs = objs.order_by('+{0}'.format(order_column))
        return count, objs[start:stop]

    def is_string(self, col_name):
        return isinstance(self.obj._fields[col_name], StringField)

    def is_integer(self, col_name):
        return isinstance(self.obj._fields[col_name], IntField)

    def is_nullable(self, col_name):
        return not self.obj._fields[col_name].required

    def is_unique(self, col_name):
        return self.obj._fields[col_name].unique

    def is_pk(self, col_name):
        return col_name == 'id'

    def add(self, item):
        try:
            item.save()
            flash(as_unicode(self.add_row_message), 'success')
            return True
        except Exception as e:
            flash(as_unicode(self.general_error_message + ' ' + str(sys.exc_info()[0])), 'danger')
            log.exception("Add record error: {0}".format(str(e)))
            return False

    def edit(self, item):
        try:
            item.save()
            flash(as_unicode(self.edit_row_message), 'success')
            return True
        except Exception as e:
            flash(as_unicode(self.general_error_message + ' ' + str(sys.exc_info()[0])), 'danger')
            log.exception("Edit record error: {0}".format(str(e)))
            return False

    def delete(self, item):
        try:
            item.delete()
            flash(as_unicode(self.delete_row_message), 'success')
            return True
        except Exception as e:
            flash(as_unicode(self.general_error_message + ' ' + str(sys.exc_info()[0])), 'danger')
            log.exception("Delete record error: {0}".format(str(e)))
            return False


    def get_columns_list(self):
        return self.obj._fields.keys()

    def get_search_columns_list(self):
        return self.obj._fields.keys()

    def get_user_columns_list(self):
        """
            Returns all model's columns except pk or fk
        """
        ret_lst = list()
        for col_name in self.get_columns_list():
            if (not self.is_pk(col_name)) and (not self.is_fk(col_name)):
                ret_lst.append(col_name)
        return ret_lst

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
        return self.obj.objects(pk=id)[0]
