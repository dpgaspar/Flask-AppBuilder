import logging

from flask_wtf import Form
from wtforms import (BooleanField, TextField,
                       TextAreaField, IntegerField, FloatField, DateField, DateTimeField)

from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField

from wtforms import validators
#from flask_wtf import validators
from .fieldwidgets import (BS3TextAreaFieldWidget,
                          BS3TextFieldWidget,
                          DatePickerWidget,
                          DateTimePickerWidget,
                          Select2Widget,
                          Select2ManyWidget)
from .models.filters import Filters
from .upload import (BS3FileUploadFieldWidget,
                    BS3ImageUploadFieldWidget,
                    FileUploadField,
                    ImageUploadField)
from .validators import Unique



log = logging.getLogger(__name__)


class FieldConverter(object):
    conversion_table = (('is_image', ImageUploadField, BS3ImageUploadFieldWidget),
                        ('is_file', FileUploadField, BS3FileUploadFieldWidget),
                        ('is_text', TextAreaField, BS3TextAreaFieldWidget),
                        ('is_string', TextField, BS3TextFieldWidget),
                        ('is_integer', IntegerField, BS3TextFieldWidget),
                        ('is_float', FloatField, BS3TextFieldWidget),
                        ('is_boolean', BooleanField, None),
                        ('is_date', DateField, DatePickerWidget),
                        ('is_datetime', DateTimeField, DateTimePickerWidget),
    )


    def __init__(self, datamodel, colname, label, description, validators, default = None):
        self.datamodel = datamodel
        self.colname = colname
        self.label = label
        self.description = description
        self.validators = validators
        self.default = default

    def convert(self):
        for conversion in self.conversion_table:
            if getattr(self.datamodel, conversion[0])(self.colname):
                if conversion[2]:
                    return conversion[1](self.label,
                                         description=self.description,
                                         validators=self.validators,
                                         widget=conversion[2](),
                                         default=self.default)
                else:
                    return conversion[1](self.label,
                                         description=self.description,
                                         validators=self.validators,
                                         default=self.default)
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

    def _get_func_related_query(self, col_name, filter_rel_fields):
        if filter_rel_fields:
            for filter_rel_field in filter_rel_fields:
                if filter_rel_field[0] == col_name:
                    sqla = filter_rel_field[1]
                    _filters = Filters().add_filter_list(sqla, filter_rel_field[2])
                    return lambda: sqla.query(_filters)[1]
        rel_model = self.datamodel.get_model_relation(col_name)
        return lambda: self.datamodel.session.query(rel_model)


    def _convert_many_to_one(self, col_name, label, description,
                             lst_validators, filter_rel_fields, form_props):
        query_func = self._get_func_related_query(col_name, filter_rel_fields)
        allow_blank = True
        col = self.datamodel.get_relation_fk(col_name)
        if not col.nullable:
            lst_validators.append(validators.Required())
            allow_blank = False
        else:
            lst_validators.append(validators.Optional())
        form_props[col_name] = \
            QuerySelectField(label,
                             description=description,
                             query_factory=query_func,
                             allow_blank=allow_blank,
                             validators=lst_validators,
                             widget=Select2Widget())
        return form_props

    def _convert_many_to_many(self, col_name, label, description,
                              lst_validators, filter_rel_fields, form_props):
        query_func = self._get_func_related_query(col_name, filter_rel_fields)
        allow_blank = True
        form_props[col_name] = \
            QuerySelectMultipleField(label,
                                     description=description,
                                     query_factory=query_func,
                                     allow_blank=allow_blank,
                                     validators=lst_validators,
                                     widget=Select2ManyWidget())
        return form_props

    def _convert_field(self, col_name, label, description, lst_validators, form_props):
        if not self.datamodel.is_nullable(col_name):
            lst_validators.append(validators.InputRequired())
        else:
            lst_validators.append(validators.Optional())
        if self.datamodel.is_unique(col_name):
            lst_validators.append(Unique(self.datamodel, col_name))
        default_value = self.datamodel.get_col_default(col_name)
        fc = FieldConverter(self.datamodel, col_name, label, description, lst_validators, default=default_value)
        form_props[col_name] = fc.convert()
        return form_props

    def _convert_prop(self, col_name, label, description, lst_validators, filter_rel_fields, form_props):
        if self.datamodel.is_relation(col_name):
            if self.datamodel.is_relation_many_to_one(col_name) or \
                    self.datamodel.is_relation_one_to_one(col_name):
                return self._convert_many_to_one(col_name, label,
                                                 description,
                                                 lst_validators,
                                                 filter_rel_fields, form_props)
            elif self.datamodel.is_relation_many_to_many(col_name) or \
                    self.datamodel.is_relation_one_to_many(col_name):
                return self._convert_many_to_many(col_name, label,
                                                  description,
                                                  lst_validators,
                                                  filter_rel_fields, form_props)
            else:
                log.warning("Relation {0} not supported".format(col_name))
        else:
            if not (self.datamodel.is_pk(col_name) or self.datamodel.is_fk(col_name)):
                return self._convert_field(col_name, label, description, lst_validators, form_props)


    def create_form(self, label_columns={}, inc_columns=[],
                    description_columns={}, validators_columns={},
                    extra_fields={}, filter_rel_fields=None):
        form_props = {}
        for col_name in inc_columns:
            if col_name in extra_fields:
                form_props[col_name] = extra_fields.get(col_name)
            else:
                #prop = self.datamodel.get_col_property(col)
                self._convert_prop(col_name, self._get_label(col_name, label_columns),
                                   self._get_description(col_name, description_columns),
                                   self._get_validators(col_name, validators_columns),
                                   filter_rel_fields, form_props)
        return type('DynamicForm', (DynamicForm,), form_props)


class DynamicForm(Form):
    @classmethod
    def refresh(self, obj=None):
        form = self(obj=obj)
        return form


