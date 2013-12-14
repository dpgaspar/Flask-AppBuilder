from sqlalchemy.orm.exc import NoResultFound

from wtforms import ValidationError


class Unique(object):
    """
        Checks field value unicity against specified table field.

        :param get_session:
            A function that return a SQAlchemy Session.
        :param model:
            The model to check unicity against.
        :param column:
            The unique column.
        :param message:
            The error message.
    """
    field_flags = ('unique', )

    def __init__(self, datamodel, column, message=None):
        self.datamodel = datamodel
        self.column = column
        self.message = message

    def __call__(self, form, field):
        filters = {}
        filters[self.column.name] = field.data
        count, obj = self.datamodel.query(filters)
        if (count > 0):           
            if hasattr(form,'_id') and form._id == self.datamodel.get_pk_value(obj):
                if self.message is None:
                    self.message = field.gettext(u'Already exists.')
                raise ValidationError(self.message)
        
