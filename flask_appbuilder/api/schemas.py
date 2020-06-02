from marshmallow import post_load, Schema

from ..const import (
    API_ADD_COLUMNS_RIS_KEY,
    API_ADD_TITLE_RIS_KEY,
    API_DESCRIPTION_COLUMNS_RIS_KEY,
    API_EDIT_COLUMNS_RIS_KEY,
    API_EDIT_TITLE_RIS_KEY,
    API_FILTERS_RIS_KEY,
    API_LABEL_COLUMNS_RIS_KEY,
    API_LIST_COLUMNS_RIS_KEY,
    API_LIST_TITLE_RIS_KEY,
    API_ORDER_COLUMN_RIS_KEY,
    API_ORDER_COLUMNS_RIS_KEY,
    API_ORDER_DIRECTION_RIS_KEY,
    API_PAGE_INDEX_RIS_KEY,
    API_PAGE_SIZE_RIS_KEY,
    API_PERMISSIONS_RIS_KEY,
    API_SELECT_COLUMNS_RIS_KEY,
    API_SELECT_KEYS_RIS_KEY,
    API_SHOW_COLUMNS_RIS_KEY,
    API_SHOW_TITLE_RIS_KEY,
)


class BaseModelSchema(Schema):
    """
    Extends marshmallow Schema to add functionality similar to marshmallow-sqlalchemy
    for creating and updating SQLAlchemy models on load
    """

    model_cls = None
    """Declare the SQLAlchemy model when creating a new model on load"""

    def __init__(self, *arg, **kwargs):
        super().__init__()
        self.instance = None

    @post_load
    def process(self, data, **kwargs):
        if self.instance is not None:
            for key, value in data.items():
                setattr(self.instance, key, value)
            return self.instance
        return self.model_cls(**data)

    def load(self, data, *, instance=None, **kwargs):
        self.instance = instance
        try:
            return super().load(data, **kwargs)
        finally:
            self.instance = None


get_list_schema = {
    "type": "object",
    "properties": {
        API_SELECT_KEYS_RIS_KEY: {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    API_LIST_COLUMNS_RIS_KEY,
                    API_ORDER_COLUMNS_RIS_KEY,
                    API_LABEL_COLUMNS_RIS_KEY,
                    API_DESCRIPTION_COLUMNS_RIS_KEY,
                    API_LIST_TITLE_RIS_KEY,
                    "none",
                ],
            },
        },
        API_SELECT_COLUMNS_RIS_KEY: {"type": "array", "items": {"type": "string"}},
        API_ORDER_COLUMN_RIS_KEY: {"type": "string"},
        API_ORDER_DIRECTION_RIS_KEY: {"type": "string", "enum": ["asc", "desc"]},
        API_PAGE_INDEX_RIS_KEY: {"type": "integer"},
        API_PAGE_SIZE_RIS_KEY: {"type": "integer"},
        API_FILTERS_RIS_KEY: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "col": {"type": "string"},
                    "opr": {"type": "string"},
                    "value": {
                        "anyOf": [
                            {"type": "number"},
                            {"type": "string"},
                            {"type": "boolean"},
                            {"type": "array"},
                        ]
                    },
                },
                "required": ["col", "opr", "value"],
            },
        },
    },
}

get_item_schema = {
    "type": "object",
    "properties": {
        API_SELECT_KEYS_RIS_KEY: {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    API_SHOW_COLUMNS_RIS_KEY,
                    API_DESCRIPTION_COLUMNS_RIS_KEY,
                    API_LABEL_COLUMNS_RIS_KEY,
                    API_SHOW_TITLE_RIS_KEY,
                    "none",
                ],
            },
        },
        API_SELECT_COLUMNS_RIS_KEY: {"type": "array", "items": {"type": "string"}},
    },
}

get_info_schema = {
    "type": "object",
    "properties": {
        API_SELECT_KEYS_RIS_KEY: {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    API_ADD_COLUMNS_RIS_KEY,
                    API_EDIT_COLUMNS_RIS_KEY,
                    API_FILTERS_RIS_KEY,
                    API_PERMISSIONS_RIS_KEY,
                    API_ADD_TITLE_RIS_KEY,
                    API_EDIT_TITLE_RIS_KEY,
                    "none",
                ],
            },
        },
        API_ADD_COLUMNS_RIS_KEY: {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    API_PAGE_SIZE_RIS_KEY: {"type": "integer"},
                    API_PAGE_INDEX_RIS_KEY: {"type": "integer"},
                },
            },
        },
        API_EDIT_COLUMNS_RIS_KEY: {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    API_PAGE_SIZE_RIS_KEY: {"type": "integer"},
                    API_PAGE_INDEX_RIS_KEY: {"type": "integer"},
                },
            },
        },
    },
}
