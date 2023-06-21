from typing import Any, Callable, Dict, List, Optional, Type

from flask_appbuilder.models.sqla import Model
from flask_appbuilder.models.sqla.interface import SQLAInterface
from marshmallow import fields, Schema
from marshmallow.fields import Field
from marshmallow_sqlalchemy import field_for
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class TreeNode:
    def __init__(self, name: str) -> None:
        self.name = name
        self.children: List["TreeNode"] = []

    def __repr__(self) -> str:
        return f"{self.name}.{str(self.children)}"


class Tree:
    """
    Simplistic one level Tree
    """

    def __init__(self) -> None:
        self.root = TreeNode("+")

    def add(self, name: str) -> None:
        node = TreeNode(name)
        self.root.children.append(node)

    def add_child(self, parent: str, name: str) -> None:
        node = TreeNode(name)
        for child in self.root.children:
            if child.name == parent:
                child.children.append(node)
                return
        root = TreeNode(parent)
        self.root.children.append(root)
        root.children.append(node)

    def __repr__(self) -> str:
        ret = ""
        for node in self.root.children:
            ret += str(node)
        return ret


def columns2Tree(columns: List[str]) -> Tree:
    tree = Tree()
    for column in columns:
        if "." in column:
            parent, child = column.split(".")
            tree.add_child(parent, child)
        else:
            tree.add(column)
    return tree


class BaseModel2SchemaConverter(object):
    def __init__(
        self,
        datamodel: SQLAInterface,
        validators_columns: Dict[str, Callable[[Any], Any]],
    ):
        """
        :param datamodel: SQLAInterface
        """
        self.datamodel = datamodel
        self.validators_columns = validators_columns

    def convert(
        self,
        columns: List[str],
        model: Optional[Type[Model]] = None,
        nested: bool = True,
        parent_schema_name: Optional[str] = None,
    ) -> SQLAlchemyAutoSchema:
        pass


class Model2SchemaConverter(BaseModel2SchemaConverter):
    """
    Class that converts Models to marshmallow Schemas
    """

    def __init__(
        self,
        datamodel: SQLAInterface,
        validators_columns: Dict[str, Callable[[Any], Any]],
    ):
        """
        :param datamodel: SQLAInterface
        """
        super(Model2SchemaConverter, self).__init__(datamodel, validators_columns)

    @staticmethod
    def _debug_schema(schema: SQLAlchemyAutoSchema) -> None:
        for k, v in schema._declared_fields.items():
            print(k, v)

    def _meta_schema_factory(
        self,
        columns: List[str],
        model: Optional[Type[Model]],
        class_mixin: Type[Schema],
        parent_schema_name: Optional[str] = None,
    ) -> Type[SQLAlchemyAutoSchema]:
        """
        Creates ModelSchema marshmallow-sqlalchemy

        :param columns: a list of columns to mix
        :param model: Model
        :param class_mixin: a marshamallow Schema to mix
        :return: ModelSchema
        """
        _model = model
        _parent_schema_name = parent_schema_name
        if columns:

            class MetaSchema(SQLAlchemyAutoSchema, class_mixin):  # type: ignore
                class Meta:
                    model = _model
                    fields = columns
                    load_instance = True
                    sqla_session = self.datamodel.session
                    # The parent_schema_name is useful to humanize nested schema names
                    # This name comes from ModelRestApi
                    parent_schema_name = _parent_schema_name

            return MetaSchema

        class MetaSchema(SQLAlchemyAutoSchema, class_mixin):  # type: ignore
            class Meta:
                model = _model
                load_instance = True
                sqla_session = self.datamodel.session
                # The parent_schema_name is useful to humanize nested schema names
                # This name comes from ModelRestApi
                parent_schema_name = _parent_schema_name

        return MetaSchema

    def _column2enum(self, datamodel: SQLAInterface, column: TreeNode) -> Field:
        required = not datamodel.is_nullable(column.name)
        sqla_column = datamodel.list_columns[column.name]
        # get SQLAlchemy column user info, we use it to get the marshmallow enum options
        column_info = sqla_column.info
        # TODO: Default should be False, but keeping this to True to keep compatibility
        # Turn this to False in the next major release
        by_value = column_info.get("marshmallow_by_value", True)
        # Get the original enum class from SQLAlchemy Enum field
        enum_class = sqla_column.type.enum_class
        if not enum_class:
            field = field_for(datamodel.obj, column.name)
        else:
            field = fields.Enum(enum_class, required=required, by_value=by_value)
        field.unique = datamodel.is_unique(column.name)
        return field

    def _column2relation(
        self,
        datamodel: SQLAInterface,
        column: TreeNode,
        nested: bool = False,
        parent_schema_name: Optional[str] = None,
    ) -> Field:
        if nested:
            required = not datamodel.is_nullable(column.name)
            nested_model = datamodel.get_related_model(column.name)
            lst = [item.name for item in column.children]
            nested_schema = self.convert(
                lst, nested_model, nested=False, parent_schema_name=parent_schema_name
            )
            if datamodel.is_relation_many_to_one(column.name):
                many = False
            elif datamodel.is_relation_many_to_many(column.name):
                many = True
                required = False
            elif datamodel.is_relation_one_to_many(column.name):
                many = True
            else:
                many = False
            field = fields.Nested(nested_schema, many=many, required=required)
            field.unique = datamodel.is_unique(column.name)
            return field
        # Handle bug on marshmallow-sqlalchemy
        # https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues/163
        if datamodel.is_relation_many_to_many(
            column.name
        ) or datamodel.is_relation_one_to_many(column.name):
            required = datamodel.get_info(column.name).get("required", False)
        else:
            required = not datamodel.is_nullable(column.name)
        field = field_for(datamodel.obj, column.name)
        field.required = required
        field.unique = datamodel.is_unique(column.name)
        return field

    def _column2field(
        self,
        datamodel: SQLAInterface,
        column: TreeNode,
        nested: bool = True,
        parent_schema_name: Optional[str] = None,
    ) -> Field:
        """

        :param datamodel: SQLAInterface
        :param column: TreeNode column (childs are dotted columns)
        :param nested: Boolean if will create nested fields
        :return: Schema.field
        """
        # Handle relations
        if datamodel.is_relation(column.name):
            return self._column2relation(
                datamodel, column, nested=nested, parent_schema_name=parent_schema_name
            )
        # Handle Enums
        if datamodel.is_enum(column.name):
            return self._column2enum(datamodel, column)
        # is custom property method field?
        if hasattr(getattr(datamodel.obj, column.name), "fget"):
            return fields.Raw(dump_only=True)
        # its a model function
        if hasattr(getattr(datamodel.obj, column.name), "__call__"):
            return fields.Function(getattr(datamodel.obj, column.name), dump_only=True)
        # is a normal model field not a function?
        if not hasattr(getattr(datamodel.obj, column.name), "__call__"):
            field = field_for(datamodel.obj, column.name)
            field.unique = datamodel.is_unique(column.name)
            if column.name in self.validators_columns:
                if field.validate is None:
                    field.validate = []
                field.validate.append(self.validators_columns[column.name])
                field.validators.append(self.validators_columns[column.name])
            return field

    def convert(
        self,
        columns: List[str],
        model: Optional[Type[Model]] = None,
        nested: bool = True,
        parent_schema_name: Optional[str] = None,
    ) -> SQLAlchemyAutoSchema:
        """
            Creates a Marshmallow ModelSchema class


        :param columns: List with columns to include, if empty converts all on model
        :param model: Override Model to convert
        :param nested: Generate relation with nested schemas
        :return: ModelSchema object
        """
        super(Model2SchemaConverter, self).convert(
            columns, model=model, nested=nested, parent_schema_name=parent_schema_name
        )

        class SchemaMixin:
            pass

        _model = model or self.datamodel.obj
        _datamodel = self.datamodel.__class__(_model)

        ma_sqla_fields_override = {}

        _columns = list()
        tree_columns = columns2Tree(columns)
        for column in tree_columns.root.children:
            # Get child model is column is dotted notation
            ma_sqla_fields_override[column.name] = self._column2field(
                _datamodel, column, nested, parent_schema_name=parent_schema_name
            )
            _columns.append(column.name)
        for k, v in ma_sqla_fields_override.items():
            setattr(SchemaMixin, k, v)
        return self._meta_schema_factory(
            _columns, _model, SchemaMixin, parent_schema_name=parent_schema_name
        )()
