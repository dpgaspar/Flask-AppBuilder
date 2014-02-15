import logging

from flask_wtf import (Form, BooleanField, TextField,
                       TextAreaField, IntegerField, DateField, QuerySelectField,
                       QuerySelectMultipleField)

from flask_wtf import validators
from upload import (BS3FileUploadFieldWidget,
                    BS3ImageUploadFieldWidget,
                    FileUploadField,
                    ImageUploadField)
from validators import Unique
from fieldwidgets import (BS3TextAreaFieldWidget,
                          BS3TextFieldWidget,
                          DatePickerWidget,
                          DateTimePickerWidget,
                          Select2Widget,
                          Select2ManyWidget)
from .models.filters import Filters
from .models.datamodel import SQLAModel

log = logging.getLogger(__name__)


class FieldConverter(object):
    conversion_table = (('is_image', ImageUploadField, BS3ImageUploadFieldWidget),
                        ('is_file', FileUploadField, BS3FileUploadFieldWidget),
                        ('is_text', TextAreaField, BS3TextAreaFieldWidget),
                        ('is_string', TextField, BS3TextFieldWidget),
                        ('is_integer', IntegerField, BS3TextFieldWidget),
                        ('is_boolean', BooleanField, None),
                        ('is_date', DateField, DatePickerWidget),
                        ('is_datetime', DateField, DateTimePickerWidget),
    )


    def __init__(self, datamodel, colname, label, description, validators):
        self.datamodel = datamodel
        self.colname = colname
        self.label = label
        self.description = description
        self.validators = validators

    def convert(self):
        for conversion in self.conversion_table:
            if getattr(self.datamodel, conversion[0])(self.colname):
                if conversion[2]:
                    return conversion[1](self.label,
                                         description=self.description,
                                         validators=self.validators,
                                         widget=conversion[2]())
                else:
                    return conversion[1](self.label,
                                         description=self.description,
                                         validators=self.validators)
        log.error('Column %s Type not supported' % self.colname)


class GeneralModelConverter(object):
    def __init__(self, datamodel):
        self.datamodel = datamodel

    def _get_validators(self, colname, validators_columns):
        if colname in validators_columns:
            return validators_columns[colname]
        else:
            return []

    def _get_description(self, colname, description_columns):
        if colname in description_columns:
            return description_columns[colname]
        else:
            return ""

    def _get_label(self, colname, label_columns):
        if colname in label_columns:
            return label_columns[colname]
        else:
            return ""

    def _get_func_related_query(self, prop, filter_rel_fields):
        if filter_rel_fields:
            for filter_rel_field in filter_rel_fields:
                if filter_rel_field[0] == prop.key:
                    sqla = filter_rel_field[1]
                    _filters = Filters().add_filter_list(sqla, filter_rel_field[2])
                    return lambda: sqla.query(_filters)[1]
        rel_model = self.datamodel.get_model_relation(prop)
        return lambda: self.datamodel.session.query(rel_model)


    def _convert_many_to_one(self, prop, label, description,
                             lst_validators, filter_rel_fields, form_props):
        query_func = self._get_func_related_query(prop, filter_rel_fields)
        allow_blank = True
        col = self.datamodel.get_relation_fk(prop)
        if not col.nullable:
            lst_validators.append(validators.Required())
            allow_blank = False
        else:
            lst_validators.append(validators.Optional())
        form_props[self.datamodel.get_property_col(prop)] = \
            QuerySelectField(label,
                             description=description,
                             query_factory=query_func,
                             allow_blank=allow_blank,
                             validators=lst_validators,
                             widget=Select2Widget())
        return form_props

    def _convert_many_to_many(self, prop, label, description,
                              lst_validators, filter_rel_fields, form_props):
        query_func = self._get_func_related_query(prop, filter_rel_fields)
        allow_blank = True
        form_props[self.datamodel.get_property_col(prop)] = \
            QuerySelectMultipleField(label,
                                     description=description,
                                     query_factory=query_func,
                                     allow_blank=allow_blank,
                                     validators=lst_validators,
                                     widget=Select2ManyWidget())
        return form_props

    def _convert_field(self, col, label, description, lst_validators, form_props):
        if not col.nullable:
            lst_validators.append(validators.Required())
        else:
            lst_validators.append(validators.Optional())
        if col.unique:
            lst_validators.append(Unique(self.datamodel, col))

        fc = FieldConverter(self.datamodel, col.name, label, description, lst_validators)
        form_props[col.name] = fc.convert()
        return form_props

    def _convert_prop(self, prop, label, description, lst_validators, filter_rel_fields, form_props):
        if self.datamodel.is_relation(prop):
            if self.datamodel.is_relation_many_to_one(prop):
                return self._convert_many_to_one(prop, label,
                                                 description,
                                                 lst_validators,
                                                 filter_rel_fields, form_props)
            if self.datamodel.is_relation_many_to_many(prop):
                return self._convert_many_to_many(prop, label,
                                                  description,
                                                  lst_validators,
                                                  filter_rel_fields, form_props)
        else:
            col = self.datamodel.get_property_first_col(prop)
            if not (self.datamodel.is_pk(col) or self.datamodel.is_fk(col)):
                return self._convert_field(col, label, description, lst_validators, form_props)


    def create_form(self, label_columns={}, inc_columns=[],
                    description_columns={}, validators_columns={},
                    extra_fields={}, filter_rel_fields=None):
        form_props = {}
        for col in inc_columns:
            if col in extra_fields:
                form_props[col] = extra_fields.get(col)
            else:
                prop = self.datamodel.get_col_property(col)
                self._convert_prop(prop, self._get_label(col, label_columns),
                                   self._get_description(col, description_columns),
                                   self._get_validators(col, validators_columns),
                                   filter_rel_fields, form_props)
        return type('DynamicForm', (DynamicForm,), form_props)


class DynamicForm(Form):
    @classmethod
    def refresh(self, obj=None):
        form = self(obj=obj)
        return form

    @classmethod
    def debug(self):
        print self.__class__.__name__
        for item in self():
            print item.name

