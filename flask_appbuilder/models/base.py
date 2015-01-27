import logging
from functools import reduce
from flask_babelpkg import lazy_gettext
from .filters import Filters

log = logging.getLogger(__name__)


class BaseInterface(object):
    """
        Base class for all data model interfaces.
        Sub class it to implement your own interface for some data engine.
    """
    obj = None

    filter_converter_class = None
    """ when sub classing override with your own custom filter converter """

    """ Messages to display on CRUD Events """
    add_row_message = lazy_gettext('Added Row')
    edit_row_message = lazy_gettext('Changed Row')
    delete_row_message = lazy_gettext('Deleted Row')
    delete_integrity_error_message = lazy_gettext('Associated data exists, please delete them first')
    add_integrity_error_message = lazy_gettext('Integrity error, probably unique constraint')
    edit_integrity_error_message = lazy_gettext('Integrity error, probably unique constraint')
    general_error_message = lazy_gettext('General Error')

    def __init__(self, obj):
        self.obj = obj

    def _get_attr_value(self, item, col):
        if not hasattr(item, col):
            # it's an inner obj attr
            return reduce(getattr, col.split('.'), item)
        if hasattr(getattr(item, col), '__call__'):
            # its a function
            return getattr(item, col)()
        else:
            # its attribute
            return getattr(item, col)

    def get_filters(self, search_columns=[]):
        return Filters(self.filter_converter_class, self, search_columns)

    def get_values_item(self, item, show_columns):
        return [self._get_attr_value(item, col) for col in show_columns]

    def get_values(self, lst, list_columns):
        """
            Get Values: formats values for list template.
            returns [{'col_name':'col_value',....},{'col_name':'col_value',....}]

            :param lst:
                The list of item objects from query
            :param list_columns:
                The list of columns to include
        """
        retlst = []
        for item in lst:
            retdict = {}
            for col in list_columns:
                retdict[col] = self._get_attr_value(item, col)
            retlst.append(retdict)
        return retlst

    """
        Returns the models class name
        usefull for auto title on views
    """
    @property
    def model_name(self):
        return self.obj.__class__.__name__

    """
        Next methods must be overridden
    """
    def query(self, filters=None, order_column='', order_direction='',
              page=None, page_size=None):
        pass

    def is_image(self, col_name):
        return False

    def is_file(self, col_name):
        return False

    def is_gridfs_file(self, col_name):
        return False

    def is_string(self, col_name):
        return False

    def is_text(self, col_name):
        return False

    def is_integer(self, col_name):
        return False

    def is_float(self, col_name):
        return False

    def is_boolean(self, col_name):
        return False

    def is_date(self, col_name):
        return False

    def is_datetime(self, col_name):
        return False

    def is_relation(self, prop):
        return False

    def is_relation_col(self, col):
        return False

    def is_relation_many_to_one(self, prop):
        return False

    def is_relation_many_to_many(self, prop):
        return False

    def is_relation_one_to_one(self, prop):
        return False

    def is_relation_one_to_many(self, prop):
        return False

    def is_nullable(self, col_name):
        return True

    def is_unique(self, col_name):
        return False

    def is_pk(self, col_name):
        return False

    def is_fk(self, col_name):
        return False

    """
    -----------------------------------------
           FUNCTIONS FOR CRUD OPERATIONS
    -----------------------------------------
    """

    def add(self, item):
        """
            Adds object
        """
        raise NotImplementedError

    def edit(self, item):
        """
            Edit (change) object
        """
        raise NotImplementedError

    def delete(self, item):
        """
            Deletes object
        """
        raise NotImplementedError

    def get_col_default(self, col_name):
        pass

    def get_keys(self, lst):
        """
            return a list of pk values from object list
        """
        pk_name = self.get_pk_name()
        return [getattr(item, pk_name) for item in lst]

    def get_pk_name(self, item):
        """
            Returns the primary key name
        """
        raise NotImplementedError

    def get_pk_value(self, item):
        return getattr(item, self.get_pk_name())

    def get(self, pk):
        """
            return the record from key
        """
        pass

    def get_related_model(self, prop):
        raise NotImplementedError

    def get_related_interface(self, col_name):
        """
            Returns a BaseInterface for the related model
            of column name.

            :param col_name: Column name with relation
            :return: BaseInterface
        """
        raise NotImplementedError

    def get_related_obj(self, col_name, value):
        raise NotImplementedError

    def get_related_fk(self, model):
        raise NotImplementedError

    def get_columns_list(self):
        """
            Returns a list of all the columns names
        """
        return []

    def get_user_columns_list(self):
        """
            Returns a list of user viewable columns names
        """
        return self.get_columns_list()

    def get_search_columns_list(self):
        """
            Returns a list of searchable columns names
        """
        return []

    def get_order_columns_list(self, list_columns=None):
        """
            Returns a list of order columns names
        """
        return []

    def get_relation_fk(self, prop):
        pass



