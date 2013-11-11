from __future__ import unicode_literals
import warnings
from wtforms import ValidationError
from sqlalchemy.orm.exc import NoResultFound


class Unique(object):
    """Checks field value unicity against specified table field.

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

    def __init__(self, get_session, model, column, message=None):
        warnings.warn('The Unique validator will be removed in WTForms 1.1', DeprecationWarning)
        self.get_session = get_session
        self.model = model
        self.column = column
        self.message = message

    def __call__(self, form, field):
        try:
            obj = self.get_session().query(self.model)\
                .filter(self.column == field.data).one()
            if not hasattr(form, '_obj') or not form._obj == obj:
                if self.message is None:
                    self.message = field.gettext('Already exists.')
                raise ValidationError(self.message)
        except NoResultFound:
            pass
