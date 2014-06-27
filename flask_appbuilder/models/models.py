__author__ = 'dpgaspar'

#--------------------------------------
#        Exceptions
#--------------------------------------
class PKMissingException(Exception):

    def __init__(self, model_name=''):
        message = 'Please set one primary key on: {0}'.format(model_name)
        super(PKMissingException, self).__init__(self, message)


class VolColumn(object):
    col_type = None
    primary_key = None
    unique = None
    nullable = None

    def __init__(self, col_type, primary_key=False, unique=False, nullable=False):
        self.col_type = col_type
        self.primary_key = primary_key
        self.unique = unique
        self.nullable = nullable

    def check_type(self, value):
        return isinstance(value, self.col_type)
    

class VolModel(object):

    def __new__(cls, *args, **kwargs):
        obj = super(VolModel, cls).__new__(cls, *args, **kwargs)
        obj._col_defs = dict()

        props = dir(obj)
        for prop in props:
            if isinstance(getattr(obj, prop), VolColumn):
                obj._col_defs[prop] = getattr(obj, prop)
                setattr(obj, prop, None)
        return obj


    def __init__(self, **kwargs):
        if not self.pk:
            # if only one column, set it as pk
            if len(self.columns) == 1:
                self._col_defs[self.columns[0]].primary_key = True
            else:
                raise PKMissingException(self._name)
        for arg in kwargs:
            if arg in self._col_defs:
                value = kwargs.get(arg)
                setattr(self, arg, value)

    def get_col_type(self, col_name):
        return self._col_defs[col_name].col_type

    @property
    def _name(self):
        """
            Returns this class name
        """
        return self.__class__.__name__

    @property
    def columns(self):
        """
            Returns a list with columns names
        """
        return self._col_defs.keys()

    @property
    def pk(self):
        """
            Returns the pk name
        """
        for col in self.columns:
            if self._col_defs[col].primary_key:
                return col


    def __repr__(self):
        return str(self)

    def __str__(self):
        str = self.__class__.__name__ + '=('
        for col in self.columns:
            str += "{0}:{1};".format(col, getattr(self,col))
        str += ')'
        return str


class BaseVolSession(object):

    def __init__(self):
        self.store = dict()

    def query(self, model_cls):
        return self.store.get(model_cls.__name__)

    def add(self, model):
        model_cls_name = model._name
        cls_list =  self.store.get(model_cls_name)
        if not cls_list:
            self.store[model_cls_name] = []
        self.store[model_cls_name].append(model)



