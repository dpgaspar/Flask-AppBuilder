import logging
from flask_babelpkg import lazy_gettext

log = logging.getLogger(__name__)


class BaseFilter(object):
    """
        Base class for all data filters.
        Sub class to im
    """
    column_name = ''
    datamodel = None
    model = None
    name = ''
    is_related_view = False
    """
        Sets this filter to a special kind for related views.
        If true this filter was not set by the user
    """

    def __init__(self, column_name, datamodel, is_related_view=False):
        """
            Constructor.

            :param column_name:
                Model field name
            :param datamodel:
                The datamodel access class
            :param is_related_view:
                Optional internal parameter to filter related views
        """
        self.column_name = column_name
        self.datamodel = datamodel
        self.model = datamodel.obj
        self.is_related_view = is_related_view

    def apply(self, query, value):
        """
            Override this to implement you own new filters
        """
        pass

    def __repr__(self):
        return self.name


class FilterRelation(BaseFilter):
    """
        Base class for all filters for relations
    """
    pass


class BaseFilterConverter(object):
    """
        Base Filter Converter, all classes responsible
        for the association of columns and possible filters
        will inherite from this

    """
    def __init__(self, datamodel):
        self.datamodel = datamodel

    def convert(self, col_name):
        for conversion in self.conversion_table:
            if getattr(self.datamodel, conversion[0])(col_name):
                return [item(col_name, self.datamodel) for item in conversion[1]]
        log.warning('Filter type not supported for column: %s' % col_name)



class BaseInterface(object):
    obj = None

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
        if hasattr(getattr(item, col), '__call__'):
            # its a function
            return getattr(item, col)()
        else:
            # its attribute
            return getattr(item, col)

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
    def get_filters(self, search_columns=None):
        pass


    def query(self, filters=None, order_column='', order_direction='',
              page=None, page_size=None):
        pass

    def is_image(self, col_name):
        return False

    def is_file(self, col_name):
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
        pass

    def edit(self, item):
        """
            Edit (change) object
        """
        pass

    def delete(self, item):
        """
            Deletes object
        """
        pass

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
        pass

    def get(self, pk):
        """
            return the record from key
        """
        pass

    def get_model_relation(self, prop):
        pass

    def get_related_obj(self, col_name, value):
        pass

    def get_related_fk(self, model):
        pass

    def get_columns_list(self):
        """
            Returns a list of all the columns names
        """
        return []

    def get_user_columns_list(self):
        """
            Returns a list user viewable columns names
        """
        return self.get_columns_list()


    def get_search_columns_list(self):
        """
            Returns a list of searchable columns names
        """
        return []

    def get_order_columns_list(self):
        """
            Returns a list of order columns names
        """
        return []

    def get_relation_fk(self, prop):
        pass



