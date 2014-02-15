# -*- coding: utf-8 -*-
import sys
import logging
import sqlalchemy as sa

from flask import flash
from flask_babelpkg import lazy_gettext
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from group import GroupByDateYear, GroupByDateMonth, GroupByCol

from mixins import FileColumn, ImageColumn
from ..filemanager import FileManager, ImageManager

log = logging.getLogger(__name__)


class DataModel():
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

    def get_gchart_json(self, lst, list_columns, label_columns):
        """
            Get google charts JSON
        """
        json_cols = []
        for col_name in list_columns:
            col = {'id': col_name, 'label': label_columns.get(col_name)}
            if self.is_string(col_name):
                col['type'] = 'string'
            elif self.is_integer(col_name):
                col['type'] = 'int'
            elif self.is_date(col_name):
                col['type'] = 'date'
            json_cols.append(col)
        json_data = []
        for item in list_columns:
            data = {}
            for col in list_columns:
                data['c'] = col
                data['v'] = self._get_attr_value(item, col)
            json_data.append(data)
        return [{'cols': json_cols, 'data': json_data}]


class SQLAModel(DataModel):
    """
    SQLAModel
    Implements SQLA support methods for views
    """
    session = None

    def __init__(self, obj, session=None):
        self.session = session
        DataModel.__init__(self, obj)


    def _get_base_query(self, query=None, filters=None, order_column='', order_direction=''):
        if filters:
            query = filters.apply_all(query)
        if order_column != '':
            query = query.order_by(order_column + ' ' + order_direction)

        return query


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
                                           filters=filters,
                                           order_column=order_column,
                                           order_direction=order_direction)

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

    """
    def query_simple_group(self, group_by = '', filters = None, order_column = '', order_direction = ''):
        if self.is_relation_col(group_by):
            rel_model, rel_direction = self._get_related_model(group_by)
            query = self.session.query(rel_model, func.count(self.obj.id))
            query = query.join(rel_model, getattr(self.obj,group_by))
            query = self._get_base_query(query = query, filters = filters, order_column = order_column, order_direction = order_direction)
            query = query.group_by(rel_model)
            return query.all()
        else:
            query = self.session.query(group_by,func.count(self.obj.id))
            query = self._get_base_query(query = query, filters = filters, order_column = order_column, order_direction = order_direction)
            query = query.group_by(group_by)
            return query.all()
    """

    def query_simple_group(self, group_by='', filters=None):
        query = self.session.query(self.obj)
        query = self._get_base_query(query=query, filters=filters)
        query_result = query.all()
        #query_result = sorted(query_result, key=lambda item: getattr(item, group_by))
        group = GroupByCol(group_by, 'Group by')
        return group.apply(query_result)


    def query_group(self, group_bys, filters=None):
        query = self.session.query(self.obj)
        query = self._get_base_query(query=query, filters=filters)
        query_result = query.all()
        for group_by in group_bys:
            result = group_by.apply2(query_result)
            log.debug("QG: %s" % result)
        return result


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
        return isinstance(self.obj.__mapper__.columns[col_name].type, ImageColumn)

    def is_file(self, col_name):
        return isinstance(self.obj.__mapper__.columns[col_name].type, FileColumn)

    def is_string(self, col_name):
        return isinstance(self.obj.__mapper__.columns[col_name].type, sa.types.String)

    def is_text(self, col_name):
        return isinstance(self.obj.__mapper__.columns[col_name].type, sa.types.Text)

    def is_integer(self, col_name):
        return isinstance(self.obj.__mapper__.columns[col_name].type, sa.types.Integer)

    def is_boolean(self, col_name):
        return isinstance(self.obj.__mapper__.columns[col_name].type, sa.types.Boolean)

    def is_date(self, col_name):
        return isinstance(self.obj.__mapper__.columns[col_name].type, sa.types.Date)

    def is_datetime(self, col_name):
        return isinstance(self.obj.__mapper__.columns[col_name].type, sa.types.DateTime)

    def is_relation(self, prop):
        return isinstance(prop, sa.orm.properties.RelationshipProperty)

    def is_relation_col(self, col):
        for i in self.get_properties_iterator():
            if self.is_relation(i):
                if (i.key == col):
                    return self.is_relation(i)
        return False

    def is_relation_many_to_one(self, prop):
        return prop.direction.name == 'MANYTOONE'

    def is_relation_many_to_many(self, prop):
        return prop.direction.name == 'MANYTOMANY'

    def is_pk(self, col):
        return col.primary_key

    def is_fk(self, col):
        return col.foreign_keys

    """
    -----------------------------------------
           FUNCTIONS FOR CRUD OPERATIONS
    -----------------------------------------
    """

    def add(self, item):
        try:
            self.session.add(item)
            self.session.commit()
            flash(unicode(self.add_row_message), 'success')
            return True
        except IntegrityError as e:
            flash(unicode(self.add_integrity_error_message), 'warning')
            log.warning("Add record integrity error")
            self.session.rollback()
            return False
        except:
            flash(unicode(self.general_error_message + ' ' + str(sys.exc_info()[0])), 'danger')
            log.exception("Add record error")
            self.session.rollback()
            return False

    def edit(self, item):
        try:
            self.session.merge(item)
            self.session.commit()
            flash(unicode(self.edit_row_message), 'success')
            return True
        except IntegrityError as e:
            flash(unicode(self.edit_integrity_error_message), 'warning')
            log.warning("Edit record integrity error")
            self.session.rollback()
            return False
        except:
            flash(unicode(self.general_error_message + ' ' + str(sys.exc_info()[0])), 'danger')
            log.exception("Edit record error")
            self.session.rollback()
            return False


    def delete(self, item):
        try:
            self._delete_files(item)
            self.session.delete(item)
            self.session.commit()
            flash(unicode(self.delete_row_message), 'success')
            return True
        except IntegrityError as e:
            flash(unicode(self.delete_integrity_error_message), 'warning')
            log.warning("Delete record integrity error")
            self.session.rollback()
            return False
        except:
            flash(unicode(self.general_error_message + ' ' + str(sys.exc_info()[0])), 'danger')
            log.exception("Delete record error")
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

    def get_model_relation(self, prop):
        return prop.mapper.class_

    def get_property_col(self, prop):
        return prop.key

    def _get_related_model(self, col_name):
        for i in self.get_properties_iterator():
            if self.is_relation(i):
                if i.key == col_name:
                    return self.get_model_relation(i), i.direction.name
        return None

    def _get_relation_direction(self, col_name):
        for i in self.get_properties_iterator():
            if self.is_relation(i):
                if i.key == col_name:
                    return i.direction.name

    def get_related_obj(self, col_name, value):
        rel_model, rel_direction = self._get_related_model(col_name)
        return self.session.query(rel_model).get(value)

    def get_related_fks(self, related_views):
        return [view.datamodel.get_related_fk(self.obj) for view in related_views]

    def get_related_fk(self, model):
        for i in self.get_properties_iterator():
            if self.is_relation(i):
                if model == self.get_model_relation(i):
                    return self.get_property_col(i)


    """
    ----------- GET METHODS -------------
    """

    def get_properties_iterator(self):
        return sa.orm.class_mapper(self.obj).iterate_properties

    def get_columns_list(self):
        ret_lst = []
        for prop in self.get_properties_iterator():
            if not self.is_relation(prop):
                if (not self.is_pk(self.get_property_first_col(prop))) and (
                        not self.is_fk(self.get_property_first_col(prop))):
                    ret_lst.append(prop.key)
            else:
                ret_lst.append(prop.key)
        return ret_lst

    #TODO get diferent solution, more intergrated with filters
    def get_search_columns_list(self):
        ret_lst = []
        for prop in self.get_properties_iterator():
            if not self.is_relation(prop):
                tmp_prop = self.get_property_first_col(prop)
                if (not self.is_pk(tmp_prop)) and (not self.is_fk(tmp_prop)):
                    col = prop.key
                    if (not self.is_image(col)) and (not self.is_file(col)):
                        ret_lst.append(col)
            else:
                ret_lst.append(prop.key)
        return ret_lst

    def get_order_columns_list(self):
        ret_lst = []
        for prop in self.get_properties_iterator():
            if not self.is_relation(prop):
                if (not self.is_pk(self.get_property_first_col(prop))) and (
                        not self.is_fk(self.get_property_first_col(prop))):
                    ret_lst.append(prop.key)
        return ret_lst

    def get_file_column_list(self):
        return [i.name for i in self.obj.__mapper__.columns if isinstance(i.type, FileColumn)]

    def get_image_column_list(self):
        return [i.name for i in self.obj.__mapper__.columns if isinstance(i.type, ImageColumn)]


    def get_property_first_col(self, prop):
        # support for only one col for pk and fk
        return prop.columns[0]

    def get_relation_fk(self, prop):
        # support for only one col for pk and fk
        return list(prop.local_columns)[0]

    def get_col_property(self, col_name):
        for prop in self.get_properties_iterator():
            if col_name == prop.key:
                return prop

    def get(self, id):
        return self.session.query(self.obj).get(id)

    def get_col_byname(self, name):
        return getattr(self.obj, name)


    """
    ----------- GET KEYS -------------------
    """

    def get_keys(self, lst):
        pk_name = self.get_pk_name()
        return [getattr(item, pk_name) for item in lst]


    """
    ----------- GET PK NAME -------------------
    """

    def get_pk_name(self):
        ret_str = ""
        for item in list(self.obj.__mapper__.columns):
            if item.primary_key:
                ret_str = item.name
                break
        return ret_str

    def get_pk_value(self, item):
        for col in list(self.obj.__mapper__.columns):
            if col.primary_key:
                return getattr(item, col.name)

    def printdebug(self):
        for item in list(self.obj.__mapper__.columns):
            print item.name, ' ', item.type, item.primary_key, item.nullable
