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
                        ]
                    },
                },
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
    },
}
