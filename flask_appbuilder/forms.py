from flask.ext.wtf import Form, fields, widgets, TextField, BooleanField, TextAreaField,IntegerField, DateField,SelectFieldBase, SelectField, QuerySelectField, QuerySelectMultipleField, HiddenField
from flask.ext.wtf import Required, Length, validators, EqualTo
from wtforms.widgets import HTMLString, html_params
import sqlalchemy as sa
from upload import *


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

    def _convert_many_to_one(self, prop, label, description, lst_validators, form_props):
        rel_model = self.datamodel.get_model_relation(prop)
        form_props[self.datamodel.get_property_col(prop)] = QuerySelectField(label,
                                                description=description,
                                                query_factory = lambda: self.datamodel.session.query(rel_model),
                                                allow_blank = True,
                                                widget=Select2Widget())
        return form_props

    def _convert_many_to_many(self, prop, label, description, lst_validators, form_props):
        rel_model = self.datamodel.get_model_relation(prop)
        form_props[self.datamodel.get_property_col(prop)] = QuerySelectMultipleField(label,
                description=description,
                query_factory = lambda: self.datamodel.session.query(rel_model),
                allow_blank=True,
                widget=Select2ManyWidget())
        return form_props

    def _convert_field(self, col, label, description, lst_validators, form_props):
        if not col.nullable:
            lst_validators.append(validators.Required())
        else:
            lst_validators.append(validators.Optional())
        if self.datamodel.is_image(col.name):
            form_props[col.name] = ImageUploadField(label,
                                    description=description,
                                    validators=lst_validators,
                                    widget=BS3ImageUploadFieldWidget())
        elif self.datamodel.is_file(col.name):
            form_props[col.name] = FileUploadField(label,
                                    description=description,
                                    validators=lst_validators,
                                    widget=BS3FileUploadFieldWidget())
        elif self.datamodel.is_text(col.name):
            form_props[col.name] = TextAreaField(label,
                                    description=description,
                                    validators=lst_validators,
                                    widget=BS3TextAreaFieldWidget())
        elif self.datamodel.is_string(col.name):
            form_props[col.name] = TextField(label,
                                    description=description,
                                    validators=lst_validators,
                                    widget=BS3TextFieldWidget())
        elif self.datamodel.is_integer(col.name):
            form_props[col.name] = IntegerField(label,
                                    description=description,
                                    validators=lst_validators,
                                    widget=BS3TextFieldWidget())
        elif self.datamodel.is_boolean(col.name):
            form_props[col.name] = BooleanField(label,
                                    description=description,
                                    validators=lst_validators)
        elif self.datamodel.is_date(col.name):
            form_props[col.name] = DateField(label,
                                                    description=description,
                                                    validators=lst_validators,
                                                    widget=DatePickerWidget())
        elif self.datamodel.is_datetime(col.name):
            form_props[col.name] = DateField(label,
                                    description=description,
                                    validators=lst_validators,
                                    widget=DateTimePickerWidget())
        else:
            print col.name + 'Column Type not supported!'
        return form_props

    def _convert_prop(self, prop, label, description, lst_validators, form_props):
        if self.datamodel.is_relation(prop):
            if self.datamodel.is_relation_many_to_one(prop):
                return self._convert_many_to_one(prop, label, description, lst_validators, form_props)
            if self.datamodel.is_relation_many_to_many(prop):
                return self._convert_many_to_many(prop, label, description, lst_validators, form_props)
        else:
            col = self.datamodel.get_property_first_col(prop)
            if not (self.datamodel.is_pk(col) or self.datamodel.is_fk(col)):
                return self._convert_field(col, label, description, lst_validators, form_props)


    def create_form(self, label_columns = {}, description_columns = {} ,validators_columns = {}, inc_columns = []):
        form_props = {}
        for col in inc_columns:
            prop = self.datamodel.get_col_property(col)
            self._convert_prop(prop, self._get_label(col, label_columns),
            self._get_description(col, description_columns),
            self._get_validators(col, validators_columns), form_props)
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

#------------------------------------------
#         WIDGETS
#------------------------------------------
class DatePickerWidget(object):
    """
    Date Time picker from Eonasdan GitHub

    """
    data_template = ('<div class="input-group date" id="datepicker">'
                    '<span class="input-group-addon"><span class="glyphicon glyphicon-calendar"></span>'
                    '</span>'
                    '<input class="form-control" data-format="yyyy-MM-dd" %(text)s/>'
                    '</div>'
                    )

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.name)
        template = self.data_template

        return HTMLString(template % {'text': html_params(type='text',
                                      value=field.data,
                                      **kwargs)
                                      })


class DateTimePickerWidget(object):
    """
    Date Time picker from Eonasdan GitHub

    """
    data_template = ('<div class="input-group date" id="datetimepicker">'
                    '<span class="input-group-addon"><span class="glyphicon glyphicon-calendar"></span>'
                    '</span>'
                    '<input class="form-control" data-format="yyyy-MM-dd hh:mm:ss" %(text)s/>'
        '</div>'
        )

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.name)
        template = self.data_template

        return HTMLString(template % {'text': html_params(type='text',
                                        value=field.data,
                                        **kwargs)
                                })




class BS3TextFieldWidget(widgets.TextInput):
    def __call__(self, field, **kwargs):
        kwargs['class'] = u'form-control'
        if field.label:
            kwargs['placeholder'] = field.label.text
        return super(BS3TextFieldWidget, self).__call__(field, **kwargs)

class BS3TextAreaFieldWidget(widgets.TextArea):
    def __call__(self, field, **kwargs):
        kwargs['class'] = u'form-control'
        kwargs['rows'] = 3
        if field.label:
            kwargs['placeholder'] = field.label.text
        return super(BS3TextAreaFieldWidget, self).__call__(field, **kwargs)

class BS3PasswordFieldWidget(widgets.PasswordInput):
    def __call__(self, field, **kwargs):
        kwargs['class'] = u'form-control'
        if field.label:
            kwargs['placeholder'] = field.label.text
        return super(BS3PasswordFieldWidget, self).__call__(field, **kwargs)


class Select2Widget(widgets.Select):
    def __call__(self, field, **kwargs):
        kwargs['class'] = u'my_select2'
        kwargs['style'] = u'width:250px'
        kwargs['data-placeholder'] = u'Select Value'
        return super(Select2Widget, self).__call__(field, **kwargs)

class Select2ManyWidget(widgets.Select):
    def __call__(self, field, **kwargs):
        kwargs['class'] = u'my_select2'
        kwargs['style'] = u'width:250px'
        kwargs['data-placeholder'] = u'Select Value'
        kwargs['multiple'] = u'true'
        return super(Select2ManyWidget, self).__call__(field, **kwargs)
