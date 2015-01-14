from __future__ import unicode_literals

import operator

from wtforms import widgets
from wtforms.compat import text_type, string_types
from wtforms.fields import SelectFieldBase
from wtforms.validators import ValidationError


class QuerySelectField(SelectFieldBase):
    """
        Based on WTForms QuerySelectField
    """
    widget = widgets.Select()

    def __init__(self, label=None, validators=None, query_func=None,
                 get_pk_func=None, get_label=None, allow_blank=False,
                 blank_text='', **kwargs):
        super(QuerySelectField, self).__init__(label, validators, **kwargs)
        self.query_func = query_func
        self.get_pk_func = get_pk_func

        if get_label is None:
            self.get_label = lambda x: x
        elif isinstance(get_label, string_types):
            self.get_label = operator.attrgetter(get_label)
        else:
            self.get_label = get_label

        self.allow_blank = allow_blank
        self.blank_text = blank_text
        self._object_list = None

    def _get_data(self):
        if self._formdata is not None:
            for pk, obj in self._get_object_list():
                if pk == self._formdata:
                    self._set_data(obj)
                    break
        return self._data

    def _set_data(self, data):
        self._data = data
        self._formdata = None

    data = property(_get_data, _set_data)

    def _get_object_list(self):
        if self._object_list is None:
            objs = self.query_func()
            self._object_list = list((text_type(self.get_pk_func(obj)), obj) for obj in objs)
        return self._object_list

    def iter_choices(self):
        if self.allow_blank:
            yield ('__None', self.blank_text, self.data is None)

        for pk, obj in self._get_object_list():
            yield (pk, self.get_label(obj), obj == self.data)

    def process_formdata(self, valuelist):
        if valuelist:
            if self.allow_blank and valuelist[0] == '__None':
                self.data = None
            else:
                self._data = None
                self._formdata = valuelist[0]

    def pre_validate(self, form):
        data = self.data
        if data is not None:
            for pk, obj in self._get_object_list():
                if data == obj:
                    break
            else:
                raise ValidationError(self.gettext('Not a valid choice'))
        elif self._formdata or not self.allow_blank:
            raise ValidationError(self.gettext('Not a valid choice'))


class QuerySelectMultipleField(QuerySelectField):
    """
    Very similar to QuerySelectField with the difference that this will
    display a multiple select. The data property will hold a list with ORM
    model instances and will be an empty list when no value is selected.
    If any of the items in the data list or submitted form data cannot be
    found in the query, this will result in a validation error.
    """
    widget = widgets.Select(multiple=True)

    def __init__(self, label=None, validators=None, default=None, **kwargs):
        if default is None:
            default = []
        super(QuerySelectMultipleField, self).__init__(label, validators, default=default, **kwargs)
        if kwargs.get('allow_blank', False):
            import warnings
            warnings.warn('allow_blank=True does not do anything for QuerySelectMultipleField.')
        self._invalid_formdata = False

    def _get_data(self):
        formdata = self._formdata
        if formdata is not None:
            data = []
            for pk, obj in self._get_object_list():
                if not formdata:
                    break
                elif pk in formdata:
                    formdata.remove(pk)
                    data.append(obj)
            if formdata:
                self._invalid_formdata = True
            self._set_data(data)
        return self._data

    def _set_data(self, data):
        self._data = data
        self._formdata = None

    data = property(_get_data, _set_data)

    def iter_choices(self):
        for pk, obj in self._get_object_list():
            yield (pk, self.get_label(obj), obj in self.data)

    def process_formdata(self, valuelist):
        self._formdata = set(valuelist)

    def pre_validate(self, form):
        if self._invalid_formdata:
            raise ValidationError(self.gettext('Not a valid choice'))
        elif self.data:
            obj_list = list(x[1] for x in self._get_object_list())
            if not isinstance(self.data, list):
                self.data = [self.data]
            for v in self.data:
                if v not in obj_list:
                    raise ValidationError(self.gettext('Not a valid choice'))


