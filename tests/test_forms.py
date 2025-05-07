import os
import unittest

from flask import Flask
from flask_appbuilder import AppBuilder, Model, SQLA
from flask_appbuilder.forms import GeneralModelConverter
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    # Enum,
    Float,
    Integer,
    Numeric,
    String,
    Text,
)
from wtforms import (
    BooleanField,
    DateField,
    DateTimeField,
    DecimalField,
    FloatField,
    IntegerField,
    StringField,
    TextAreaField,
)


class FieldsModel(Model):
    id = Column(Integer, primary_key=True)
    field_boolean = Column(Boolean())
    field_date = Column(Date())
    field_datetime = Column(DateTime())
    # Enum is broken: "PostgreSQL ENUM type requires a name."
    # field_enum = Column(Enum())
    field_float = Column(Float())
    field_integer = Column(Integer())
    field_numeric_scale0 = Column(Numeric())
    field_numeric_scale2 = Column(Numeric(scale=2))
    field_numeric_scale4 = Column(Numeric(scale=4))
    field_string = Column(String(256))
    field_text = Column(Text)


class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config.from_object("tests.config_api")

        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

    def test_model_without_context(self):
        datamodel = SQLAInterface(FieldsModel)
        conv = GeneralModelConverter(datamodel)
        columns = [
            "field_boolean",
            "field_date",
            "field_datetime",
            # "field_enum",
            "field_float",
            "field_integer",
            "field_numeric_scale0",
            "field_numeric_scale2",
            "field_numeric_scale4",
            "field_string",
            "field_text",
        ]
        form = conv.create_form(None, columns)
        self.assertTrue(form.field_boolean.field_class is BooleanField)
        self.assertTrue(form.field_date.field_class is DateField)
        self.assertTrue(form.field_datetime.field_class is DateTimeField)
        # self.assertTrue(form.field_enum.field_class is EnumField)
        self.assertTrue(form.field_float.field_class is FloatField)
        self.assertTrue(form.field_integer.field_class is IntegerField)
        print(form.field_numeric_scale0.kwargs["places"])
        self.assertTrue(
            form.field_numeric_scale0.field_class is DecimalField
            and not form.field_numeric_scale0.kwargs["places"]
        )
        self.assertTrue(
            form.field_numeric_scale2.field_class is DecimalField
            and form.field_numeric_scale2.kwargs["places"] == 2
        )
        self.assertTrue(
            form.field_numeric_scale4.field_class is DecimalField
            and form.field_numeric_scale4.kwargs["places"] == 4
        )
        self.assertTrue(form.field_string.field_class is StringField)
        self.assertTrue(form.field_text.field_class is TextAreaField)

    def test_model_with_context(self):
        datamodel = SQLAInterface(FieldsModel)
        conv = GeneralModelConverter(datamodel)
        columns = [
            "field_boolean",
            "field_date",
            "field_datetime",
            # "field_enum",
            "field_float",
            "field_integer",
            "field_numeric_scale0",
            "field_numeric_scale2",
            "field_numeric_scale4",
            "field_string",
            "field_text",
        ]
        with self.appbuilder.get_app.test_request_context():
            form = conv.create_form(None, columns)()
            self.assertTrue(isinstance(form.field_boolean, BooleanField))
            self.assertTrue(isinstance(form.field_date, DateField))
            self.assertTrue(isinstance(form.field_datetime, DateTimeField))
            # self.assertTrue(isinstance(form.field_enum, EnumField))
            self.assertTrue(isinstance(form.field_float, FloatField))
            self.assertTrue(isinstance(form.field_integer, IntegerField))
            self.assertTrue(
                isinstance(form.field_numeric_scale0, DecimalField)
                and not form.field_numeric_scale0.places
            )
            self.assertTrue(
                isinstance(form.field_numeric_scale2, DecimalField)
                and form.field_numeric_scale2.places == 2
            )
            self.assertTrue(
                isinstance(form.field_numeric_scale4, DecimalField)
                and form.field_numeric_scale4.places == 4
            )
            self.assertTrue(isinstance(form.field_string, StringField))
            self.assertTrue(isinstance(form.field_text, TextAreaField))
