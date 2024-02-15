from flask_babel import lazy_gettext as _
from markupsafe import Markup
from wtforms import widgets
from wtforms.widgets import html_params


class DatePickerWidget:
    """
    Date Time picker from Eonasdan GitHub

    """

    data_template = (
        '<div class="input-group date appbuilder_date"'
        ' data-provide="datepicker" id="datepicker">'
        '<span class="input-group-addon"><i class="fa fa-calendar cursor-hand"></i>'
        "</span>"
        '<input class="form-control" data-format="yyyy-MM-dd" %(text)s />'
        "</div>"
    )

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("name", field.name)
        if not field.data:
            field.data = ""
        template = self.data_template

        return Markup(
            template % {"text": html_params(type="text", value=field.data, **kwargs)}
        )


class DateTimePickerWidget:
    """
    Date Time picker from Eonasdan GitHub

    """

    data_template = (
        '<div class="input-group date appbuilder_datetime" '
        'data-provide="datepicker" id="datetimepicker">'
        '<span class="input-group-addon"><i class="fa fa-calendar cursor-hand"></i>'
        "</span>"
        '<input class="form-control" data-format="yyyy-MM-dd hh:mm:ss" %(text)s />'
        "</div>"
    )

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("name", field.name)
        if not field.data:
            field.data = ""
        template = self.data_template

        return Markup(
            template % {"text": html_params(type="text", value=field.data, **kwargs)}
        )


class BS3TextFieldWidget(widgets.TextInput):
    def __call__(self, field, **kwargs):
        kwargs["class"] = "form-control"
        if field.label:
            kwargs["placeholder"] = field.label.text
        if "name_" in kwargs:
            field.name = kwargs["name_"]
        return super(BS3TextFieldWidget, self).__call__(field, **kwargs)


class BS3TextAreaFieldWidget(widgets.TextArea):
    def __call__(self, field, **kwargs):
        kwargs["class"] = "form-control"
        kwargs["rows"] = 3
        if field.label:
            kwargs["placeholder"] = field.label.text
        return super(BS3TextAreaFieldWidget, self).__call__(field, **kwargs)


class BS3PasswordFieldWidget(widgets.PasswordInput):
    def __call__(self, field, **kwargs):
        kwargs["class"] = "form-control"
        if field.label:
            kwargs["placeholder"] = field.label.text
        return super(BS3PasswordFieldWidget, self).__call__(field, **kwargs)


class Select2AJAXWidget:
    data_template = "<input %(text)s />"

    def __init__(self, endpoint, extra_classes=None, style=None):
        self.endpoint = endpoint
        self.extra_classes = extra_classes
        self.style = style or ""

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("name", field.name)
        kwargs.setdefault("endpoint", self.endpoint)
        if self.style:
            kwargs.setdefault("style", self.style)
        input_classes = "input-group my_select2_ajax"
        if self.extra_classes:
            input_classes = input_classes + " " + self.extra_classes
        kwargs.setdefault("class", input_classes)
        if not field.data:
            field.data = ""
        template = self.data_template

        return Markup(
            template % {"text": html_params(type="text", value=field.data, **kwargs)}
        )


class Select2SlaveAJAXWidget:
    data_template = '<input class="input-group my_select2_ajax_slave" %(text)s />'

    def __init__(self, master_id, endpoint, extra_classes=None, style=None):
        self.endpoint = endpoint
        self.master_id = master_id
        self.extra_classes = extra_classes
        self.style = style or ""

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("name", field.name)
        kwargs.setdefault("endpoint", self.endpoint)
        kwargs.setdefault("master_id", self.master_id)
        if self.style:
            kwargs.setdefault("style", self.style)
        input_classes = "input-group my_select2_ajax"
        if self.extra_classes:
            input_classes = input_classes + " " + self.extra_classes
        kwargs.setdefault("class", input_classes)

        if not field.data:
            field.data = ""
        template = self.data_template

        return Markup(
            template % {"text": html_params(type="text", value=field.data, **kwargs)}
        )


class Select2Widget(widgets.Select):
    extra_classes = None

    def __init__(self, extra_classes=None, style=None):
        self.extra_classes = extra_classes
        self.style = style
        super(Select2Widget, self).__init__()

    def __call__(self, field, **kwargs):
        kwargs["class"] = "my_select2 form-control"
        if self.extra_classes:
            kwargs["class"] = kwargs["class"] + " " + self.extra_classes
        if self.style:
            kwargs["style"] = self.style
        kwargs["data-placeholder"] = _("Select Value")
        if "name_" in kwargs:
            field.name = kwargs["name_"]
        return super(Select2Widget, self).__call__(field, **kwargs)


class Select2ManyWidget(widgets.Select):
    extra_classes = None

    def __init__(self, extra_classes=None, style=None):
        self.extra_classes = extra_classes
        self.style = style
        super(Select2ManyWidget, self).__init__()

    def __call__(self, field, **kwargs):
        kwargs["class"] = "my_select2 form-control"
        if self.extra_classes:
            kwargs["class"] = kwargs["class"] + " " + self.extra_classes
        if self.style:
            kwargs["style"] = self.style
        kwargs["data-placeholder"] = _("Select Value")
        kwargs["multiple"] = "true"
        if "name_" in kwargs:
            field.name = kwargs["name_"]
        return super(Select2ManyWidget, self).__call__(field, **kwargs)
