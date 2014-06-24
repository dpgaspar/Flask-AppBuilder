__author__ = 'dpgaspar'


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



class VolModel(object):

    def __new__(cls, *args, **kwargs):
        obj = super(VolModel, cls).__new__(cls, *args, **kwargs)
        obj.col_defs = dict()

        props = dir(obj)
        for prop in props:
            if isinstance(getattr(obj,prop), VolColumn):
                obj.col_defs[prop] = getattr(obj, prop)
                setattr(obj, prop, None)
        return obj


    def __init__(self, **kwargs):
        for arg in kwargs:
            if arg in self.col_defs:
                value = kwargs.get(arg)
                setattr(self, arg, value)

    def get_col_type(self, col_name):
        return self.col_defs[col_name].col_type

    def get_cols(self):
        return self.col_defs.keys()

    def __repr__(self):
        return str(self)

    def __str__(self):
        str = self.__class__.__name__ + '=('
        for col in self.get_cols():
            str += "{0}:{1};".format(col, getattr(self,col))
        str += ')'
        return str


class BaseVolSession(object):

    def __init__(self):
        self.store = dict()

    def query(self, model_cls):
        return self.store.get(model_cls.__name__)

    def add(self, model):
        model_cls_name = model.__class__.__name__
        cls_list =  self.store.get(model_cls_name)
        if not cls_list:
            self.store[model_cls_name] = []
        self.store[model_cls_name].append(model)



