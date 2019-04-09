from marshmallow import fields
from marshmallow_enum import EnumField
from marshmallow_sqlalchemy import field_for
from marshmallow_sqlalchemy.schema import ModelSchema


class BaseModel2SchemaConverter(object):

    def __init__(self, datamodel, validators_columns):
        """
        :param datamodel: SQLAInterface
        """
        self.datamodel = datamodel
        self.validators_columns = validators_columns

    def convert(self, columns, **kwargs):
        pass


class Model2SchemaConverter(BaseModel2SchemaConverter):
    """
        Class that converts Models to marshmallow Schemas
    """

    def __init__(self, datamodel, validators_columns):
        """
        :param datamodel: SQLAInterface
        """
        super(Model2SchemaConverter, self).__init__(datamodel, validators_columns)

    @staticmethod
    def _debug_schema(schema):
        for k, v in schema._declared_fields.items():
            print(k, v)

    def _meta_schema_factory(self, columns, model, class_mixin):
        """
            Creates ModelSchema marshmallow-sqlalchemy

        :param columns: a list of columns to mix
        :param model: Model
        :param class_mixin: a marshamallow Schema to mix
        :return: ModelSchema
        """
        _model = model
        if columns:
            class MetaSchema(ModelSchema, class_mixin):
                class Meta:
                    model = _model
                    fields = columns
                    strict = True
                    sqla_session = self.datamodel.session
        else:
            class MetaSchema(ModelSchema, class_mixin):
                class Meta:
                    model = _model
                    strict = True
                    sqla_session = self.datamodel.session
        return MetaSchema

    def _column2field(self, datamodel, column, nested=True, enum_dump_by_name=False):
        _model = datamodel.obj
        # Handle relations
        if datamodel.is_relation(column) and nested:
            required = not datamodel.is_nullable(column)
            nested_model = datamodel.get_related_model(column)
            nested_schema = self.convert(
                [],
                nested_model,
                nested=False
            )
            if datamodel.is_relation_many_to_one(column):
                many = False
            elif datamodel.is_relation_many_to_many(column):
                many = True
            else:
                many = False
            field = fields.Nested(nested_schema, many=many, required=required)
            field.unique = datamodel.is_unique(column)
            return field
        # Handle bug on marshmallow-sqlalchemy #163
        elif datamodel.is_relation(column):
            required = not datamodel.is_nullable(column)
            field = field_for(_model, column)
            field.required = required
            field.unique = datamodel.is_unique(column)
            return field
        # Handle Enums
        elif datamodel.is_enum(column):
            required = not datamodel.is_nullable(column)
            enum_class = datamodel.list_columns[column].info.get(
                'enum_class',
                datamodel.list_columns[column].type
            )
            if enum_dump_by_name:
                enum_dump_by = EnumField.NAME
            else:
                enum_dump_by = EnumField.VALUE
            field = EnumField(enum_class, dump_by=enum_dump_by, required=required)
            field.unique = datamodel.is_unique(column)
            return field
        if not hasattr(getattr(_model, column), '__call__'):
            field = field_for(_model, column)
            field.unique = datamodel.is_unique(column)
            if column in self.validators_columns:
                field.validate.append(self.validators_columns[column])
            return field

    def convert(self, columns, model=None, nested=True, enum_dump_by_name=False):
        """
            Creates a Marshmallow ModelSchema class


        :param columns: List with columns to include, if empty converts all on model
        :param model: Override Model to convert
        :param nested: Generate relation with nested schemas
        :return: ModelSchema object
        """
        super(Model2SchemaConverter, self).convert(
            columns,
            model=model,
            nested=nested
        )

        class SchemaMixin:
            pass

        _model = model or self.datamodel.obj
        _datamodel = self.datamodel.__class__(_model)

        ma_sqla_fields_override = {}

        _columns = list()
        for column in columns:
            ma_sqla_fields_override[column] = self._column2field(
                _datamodel,
                column,
                nested,
                enum_dump_by_name
            )
            _columns.append(column)
        for k, v in ma_sqla_fields_override.items():
            setattr(SchemaMixin, k, v)
        return self._meta_schema_factory(_columns, _model, SchemaMixin)()
