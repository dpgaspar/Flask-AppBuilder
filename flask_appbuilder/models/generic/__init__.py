__author__ = 'dpgaspar'

import operator
import os


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
                vol_col = getattr(obj, prop)
                obj._col_defs[prop] = vol_col
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
        if hasattr(self, '_col_defs'):
            return self._col_defs.keys()
        else:
            return [prop for prop in dir(self)
                if isinstance(getattr(self, prop), VolColumn)]


    @property
    def properties(self):
        return self._col_defs

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
            str += "{0}:{1};".format(col, getattr(self, col))
        str += ')\n'
        return str


class BaseVolSession(object):

    def __init__(self):
        self._order_by_cmd = None
        self._filters_cmd = list()
        self.store = dict()
        self.query_filters = list()
        self.query_class = ""
        self._offset = 0
        self._limit = 0

    def clear(self):
        """
            Deletes the entire store
        """
        self.store = dict()

    def delete_all(self, model_cls):
        """
            Deletes all objects of type model_cls
        """
        self.store[model_cls._name] = []

    def get(self, pk):
        for item in self.store.get(self.query_class):
            # coverts pk value to correct type
            pk = item.properties[item.pk].col_type(pk)
            if getattr(item, item.pk) == pk:
                return item

    def query(self, model_cls):
        self._filters_cmd = list()
        self.query_filters = list()
        self._order_by_cmd = None
        self._offset = 0
        self._limit = 0
        self.query_class = model_cls._name
        return self

    def order_by(self, order_cmd):
        self._order_by_cmd = order_cmd
        return self

    def _order_by(self, data, order_cmd):
        col_name, direction = order_cmd.split()
        reverse_flag = direction == 'desc'
        return sorted(data, key=operator.attrgetter(col_name), reverse=reverse_flag)

    def scalar(self):
        return 0

    #-----------------------------------------
    #           FUNCTIONS for FILTERS
    #-----------------------------------------

    def like(self, col_name, value):
        self._filters_cmd.append((self._like, col_name, value))
        return self

    def _like(self, item, col_name, value):
        return value in getattr(item, col_name)

    def not_like(self, col_name, value):
        self._filters_cmd.append((self._not_like, col_name, value))
        return self

    def _not_like(self, item, col_name, value):
        return value not in getattr(item, col_name)

    def equal(self, col_name, value):
        self._filters_cmd.append((self._equal, col_name, value))
        return self

    def _equal(self, item, col_name, value):
        source_value = getattr(item, col_name)
        return source_value == type(source_value)(value)

    def not_equal(self, col_name, value):
        self._filters_cmd.append((self._not_equal, col_name, value))
        return self

    def _not_equal(self, item, col_name, value):
        source_value = getattr(item, col_name)
        return source_value != type(source_value)(value)


    def offset(self, offset = 0):
        self._offset = offset
        return self

    def limit(self, limit = 0):
        self._limit = limit
        return self

    def all(self):
        items = list()
        if not self._filters_cmd:
            items = self.store.get(self.query_class)
        else:
            for item in self.store.get(self.query_class):
                tmp_flag = True
                for filter_cmd in self._filters_cmd:
                    if not filter_cmd[0](item, filter_cmd[1], filter_cmd[2]):
                        tmp_flag = False
                        break
                if tmp_flag:
                    items.append(item)
        if self._order_by_cmd:
            items = self._order_by(items, self._order_by_cmd)
        total_length = len(items)
        if self._limit != 0:
            items = items[self._offset:self._offset + self._limit]
        return total_length, items

    def add(self, model):
        model_cls_name = model._name
        cls_list =  self.store.get(model_cls_name)
        if not cls_list:
            self.store[model_cls_name] = []
        self.store[model_cls_name].append(model)

#-------------------------------------
#                EXP
#-------------------------------------
class PSModel(VolModel):
    UID = VolColumn(str)
    PID = VolColumn(int, primary_key=True)
    PPID = VolColumn(int)
    C = VolColumn(int)
    STIME = VolColumn(str)
    TTY = VolColumn(str)
    TIME = VolColumn(str)
    CMD = VolColumn(str)


class PSSession(BaseVolSession):

    regexp = "(\w+) +(\w+) +(\w+) +(\w+) +(\w+:\w+|\w+) (\?|tty\w+) +(\w+:\w+:\w+) +(.+)\n"

    def add_object(self, line):
        import re
        group = re.findall(self.regexp, line)
        if group:
            model = PSModel()
            model.UID = group[0][0]
            model.PID = int(group[0][1])
            model.PPID = int(group[0][2])
            model.C = int(group[0][3])
            model.STIME = group[0][4]
            model.TTY = group[0][5]
            model.TIME = group[0][6]
            model.CMD = group[0][7]
            self.add(model)


    def get(self, pk):
        self.delete_all(PSModel())
        out = os.popen('ps -p {0} -f'.format(pk))
        for line in out.readlines():
            self.add_object(line)
        return super(PSSession, self).get(pk)


    def all(self):
        self.delete_all(PSModel())
        out = os.popen('ps -ef')
        for line in out.readlines():
            self.add_object(line)
        return super(PSSession, self).all()
