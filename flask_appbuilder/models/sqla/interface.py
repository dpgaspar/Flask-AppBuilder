# -*- coding: utf-8 -*-
import sys
import logging
import sqlalchemy as sa

from flask import flash
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from ..base import BaseInterface
from .filters import SQLAFilterConverter
from ..filters import Filters
from ..group import GroupByDateYear, GroupByDateMonth, GroupByCol
from ..mixins import FileColumn, ImageColumn
from ...filemanager import FileManager, ImageManager
from ..._compat import as_unicode

log = logging.getLogger(__name__)


class SQLAInterface(BaseInterface):
    """
    SQLAModel
    Implements SQLA support methods for views
    """
    session = None

    def __init__(self, obj, session=None):
        self.list_columns = dict()
        self.list_properties = dict()

        self.session = session
        # Collect all SQLA columns and properties
        for col_name in obj.__mapper__.columns.keys():
            self.list_columns[col_name] = obj.__mapper__.columns[col_name]
        for prop in sa.orm.class_mapper(obj).iterate_properties:
            self.list_properties[prop.key] = prop
        super(SQLAInterface, self).__init__(obj)

    @property
    def model_name(self):
        """
            Returns the models class name
            useful for auto title on views
        """
        return self.obj.__name__

    @staticmethod
    def _get_base_query(query=None, filters=None, order_column='', order_direction=''):
        if filters:
            query = filters.apply_all(query)
        if order_column != '':
            query = query.order_by(order_column + ' ' + order_direction)
        return query

    def get_filters(self, search_columns=[]):
        return Filters(SQLAFilterConverter, search_columns, self)

    def query(self, filters=None, order_column='', order_direction='',
              page=None, page_size=None):
        """
            QUERY
            :param filters:
                dict with filters {<col_name>:<value,...}
            :param order_column:
                name of the column to order
            :param order_direction:
                the direction to order <'asc'|'desc'>
            :param page:
                the current page
            :param page_size:
                the current page size

        """
        query = self.session.query(self.obj)
        query_count = self.session.query(func.count('*')).select_from(self.obj)

        query_count = self._get_base_query(query=query_count,
                                           filters=filters)

        query = self._get_base_query(query=query,
                                     filters=filters,
                                     order_column=order_column,
                                     order_direction=order_direction)

        count = query_count.scalar()

        if page:
            query = query.offset(page * page_size)
        if page_size:
            query = query.limit(page_size)

        return count, query.all()

    def query_simple_group(self, group_by='', aggregate_func = None, aggregate_col = None, filters=None):
        query = self.session.query(self.obj)
        query = self._get_base_query(query=query, filters=filters)
        query_result = query.all()
        group = GroupByCol(group_by, 'Group by')
        return group.apply(query_result)

    def query_month_group(self, group_by='', filters=None):
        query = self.session.query(self.obj)
        query = self._get_base_query(query=query, filters=filters)
        query_result = query.all()
        group = GroupByDateMonth(group_by, 'Group by Month')
        return group.apply(query_result)

    def query_year_group(self, group_by='', filters=None):
        query = self.session.query(self.obj)
        query = self._get_base_query(query=query, filters=filters)
        query_result = query.all()
        group_year = GroupByDateYear(group_by, 'Group by Year')
        return group_year.apply(query_result)

    """
    -----------------------------------------
         FUNCTIONS for Testing TYPES
    -----------------------------------------
    """

    def is_image(self, col_name):
        return isinstance(self.list_columns[col_name].type, ImageColumn)

    def is_file(self, col_name):
        return isinstance(self.list_columns[col_name].type, FileColumn)

    def is_string(self, col_name):
        return isinstance(self.list_columns[col_name].type, sa.types.String)

    def is_text(self, col_name):
        return isinstance(self.list_columns[col_name].type, sa.types.Text)

    def is_integer(self, col_name):
        return isinstance(self.list_columns[col_name].type, sa.types.Integer)

    def is_float(self, col_name):
        return isinstance(self.list_columns[col_name].type, sa.types.Float)

    def is_boolean(self, col_name):
        return isinstance(self.list_columns[col_name].type, sa.types.Boolean)

    def is_date(self, col_name):
        return isinstance(self.list_columns[col_name].type, sa.types.Date)

    def is_datetime(self, col_name):
        return isinstance(self.list_columns[col_name].type, sa.types.DateTime)


    def is_relation(self, col_name):
        return isinstance(self.list_properties[col_name], sa.orm.properties.RelationshipProperty)

    def is_relation_many_to_one(self, col_name):
        if self.is_relation(col_name):
            return self.list_properties[col_name].direction.name == 'MANYTOONE'

    def is_relation_many_to_many(self, col_name):
        if self.is_relation(col_name):
            return self.list_properties[col_name].direction.name == 'MANYTOMANY'

    def is_relation_one_to_one(self, col_name):
        if self.is_relation(col_name):
            return self.list_properties[col_name].direction.name == 'ONETOONE'

    def is_relation_one_to_many(self, col_name):
        if self.is_relation(col_name):
            return self.list_properties[col_name].direction.name == 'ONETOMANY'

    def is_nullable(self, col_name):
        try:
            return self.list_columns[col_name].nullable
        except:
            return False

    def is_unique(self, col_name):
        try:
            return self.list_columns[col_name].unique
        except:
            return False

    def is_pk(self, col_name):
        try:
            return self.list_columns[col_name].primary_key
        except:
            return False

    def is_fk(self, col_name):
        try:
            return self.list_columns[col_name].foreign_keys
        except:
            return False


    """
    -----------------------------------------
           FUNCTIONS FOR CRUD OPERATIONS
    -----------------------------------------
    """

    def add(self, item):
        try:
            self.session.add(item)
            self.session.commit()
            flash(as_unicode(self.add_row_message), 'success')
            return True
        except IntegrityError as e:
            flash(as_unicode(self.add_integrity_error_message), 'warning')
            log.warning("Add record integrity error: {0}".format(str(e)))
            self.session.rollback()
            return False
        except Exception as e:
            flash(as_unicode(self.general_error_message + ' ' + str(sys.exc_info()[0])), 'danger')
            log.exception("Add record error: {0}".format(str(e)))
            self.session.rollback()
            return False

    def edit(self, item):
        try:
            self.session.merge(item)
            self.session.commit()
            flash(as_unicode(self.edit_row_message), 'success')
            return True
        except IntegrityError as e:
            flash(as_unicode(self.edit_integrity_error_message), 'warning')
            log.warning("Edit record integrity error: {0}".format(str(e)))
            self.session.rollback()
            return False
        except Exception as e:
            flash(as_unicode(self.general_error_message + ' ' + str(sys.exc_info()[0])), 'danger')
            log.exception("Edit record error: {0}".format(str(e)))
            self.session.rollback()
            return False


    def delete(self, item):
        try:
            self._delete_files(item)
            self.session.delete(item)
            self.session.commit()
            flash(as_unicode(self.delete_row_message), 'success')
            return True
        except IntegrityError as e:
            flash(as_unicode(self.delete_integrity_error_message), 'warning')
            log.warning("Delete record integrity error: {0}".format(str(e)))
            self.session.rollback()
            return False
        except Exception as e:
            flash(as_unicode(self.general_error_message + ' ' + str(sys.exc_info()[0])), 'danger')
            log.exception("Delete record error: {0}".format(str(e)))
            self.session.rollback()
            return False

    """
    FILE HANDLING METHODS
    """

    def _add_files(self, this_request, item):
        fm = FileManager()
        im = ImageManager()
        for file_col in this_request.files:
            if self.is_file(file_col):
                fm.save_file(this_request.files[file_col], getattr(item, file_col))
        for file_col in this_request.files:
            if self.is_image(file_col):
                im.save_file(this_request.files[file_col], getattr(item, file_col))


    def _delete_files(self, item):
        for file_col in self.get_file_column_list():
            if self.is_file(file_col):
                if getattr(item, file_col):
                    fm = FileManager()
                    fm.delete_file(getattr(item, file_col))
        for file_col in self.get_image_column_list():
            if self.is_image(file_col):
                if getattr(item, file_col):
                    im = ImageManager()
                    im.delete_file(getattr(item, file_col))

    """
    -----------------------------------------
         FUNCTIONS FOR RELATED MODELS
    -----------------------------------------
    """
    def get_col_default(self, col_name):
        default = getattr(self.list_columns[col_name], 'default', None)
        if default is not None:
            value = getattr(default, 'arg', None)
            if value is not None:
                if getattr(default, 'is_callable', False):
                    return lambda: default.arg(None)
                else:
                    if not getattr(default, 'is_scalar', True):
                        return None
                return value

    def get_model_relation(self, col_name):
        return self.list_properties[col_name].mapper.class_

    def query_model_relation(self, col_name):
        model = self.get_model_relation(col_name)
        return self.session.query(model).all()

    def _get_related_model(self, col_name):
        if self.is_relation(col_name):
            return self.get_model_relation(col_name), self.list_properties[col_name].direction.name
        return None

    def get_related_obj(self, col_name, value):
        rel_model, rel_direction = self._get_related_model(col_name)
        return self.session.query(rel_model).get(value)

    def get_related_fks(self, related_views):
        return [view.datamodel.get_related_fk(self.obj) for view in related_views]

    def get_related_fk(self, model):
        for col_name in self.list_properties.keys():
            if self.is_relation(col_name):
                if model == self.get_model_relation(col_name):
                    return col_name
                    #return self.get_property_col(i)


    """
    ----------- GET METHODS -------------
    """

    def get_columns_list(self):
        """
            Returns all model's columns on SQLA properties
        """
        return list(self.list_properties.keys())

    def get_user_columns_list(self):
        """
            Returns all model's columns except pk or fk
        """
        ret_lst = list()
        for col_name in self.list_properties.keys():
            if (not self.is_pk(col_name)) and (not self.is_fk(col_name)):
                ret_lst.append(col_name)
        return ret_lst

    #TODO get different solution, more integrated with filters
    def get_search_columns_list(self):
        ret_lst = list()
        for col_name in self.list_properties.keys():
            if not self.is_relation(col_name):
                tmp_prop = self.get_property_first_col(col_name).name
                if (not self.is_pk(tmp_prop)) and \
                        (not self.is_fk(tmp_prop)) and \
                        (not self.is_image(col_name)) and \
                        (not self.is_file(col_name)) and \
                        (not self.is_boolean(col_name)):
                    ret_lst.append(col_name)
            else:
                ret_lst.append(col_name)
        return ret_lst

    def get_order_columns_list(self):
        ret_lst = list()
        for col_name in self.list_properties.keys():
            if not self.is_relation(col_name):
                ret_lst.append(col_name)
        return ret_lst

    def get_file_column_list(self):
        return [i.name for i in self.obj.__mapper__.columns if isinstance(i.type, FileColumn)]

    def get_image_column_list(self):
        return [i.name for i in self.obj.__mapper__.columns if isinstance(i.type, ImageColumn)]


    def get_property_first_col(self, col_name):
        # support for only one col for pk and fk
        return self.list_properties[col_name].columns[0]

    def get_relation_fk(self, col_name):
        # support for only one col for pk and fk
        return list(self.list_properties[col_name].local_columns)[0]

    def get(self, id):
        return self.session.query(self.obj).get(id)


    """
    ----------- GET PK NAME -------------------
    """
    def get_pk_name(self):
        for col_name in self.list_columns.keys():
            if self.is_pk(col_name):
                return col_name

    def get_pk_value(self, item):
        for col_name in self.list_columns.keys():
            if self.is_pk(col_name):
                return getattr(item, col_name)

"""
    For Retro-Compatibility
"""
SQLModel = SQLAInterface
