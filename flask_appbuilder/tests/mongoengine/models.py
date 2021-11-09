from mongoengine import (
    DateTimeField,
    FileField,
    FloatField,
    ImageField,
    IntField,
    ReferenceField,
    StringField,
)
from mongoengine import Document


class Model1(Document):
    field_string = StringField(unique=True, required=True)
    field_integer = IntField()
    field_float = FloatField()
    field_date = DateTimeField()
    field_file = FileField()
    field_image = ImageField()

    def __repr__(self):
        return str(self.field_string)

    def __unicode__(self):
        return self.field_string


class Model2(Document):
    field_string = StringField(unique=True, required=True)
    field_integer = IntField()
    field_float = FloatField()
    field_date = DateTimeField()
    excluded_string = StringField(default="EXCLUDED")
    default_string = StringField(default="DEFAULT")
    group = ReferenceField(Model1, required=True)

    def __repr__(self):
        return str(self.field_string)

    def field_method(self):
        return "field_method_value"
