
get_list_schema = {
    "type": "object",
    "properties": {
        "keys": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "list_columns",
                    "order_columns",
                    "label_columns",
                    "description_columns",
                    "none"
                ]
            }
        },
        "columns": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "order_column": {
            "type": "string"
        },
        "order_direction": {
            "type": "string",
            "enum": ["asc", "desc"]
        },
        "page": {
            "type": "integer"
        },
        "page_size": {
            "type": "integer"
        },
        "filters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "col": {
                        "type": "string"
                    },
                    "opr": {
                        "type": "string"
                    },
                    "value": {
                        "type": ["number", "string", "boolean", "null"]
                    }
                }
            }
        }
    }
}

get_item_schema = {
    "type": "object",
    "properties": {
        "keys": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "show_columns",
                    "description_columns",
                    "label_columns",
                    "none"
                ]
            }
        },
        "columns": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    }
}

get_info_schema = {
    "type": "object",
    "properties": {
        "keys": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "add_columns",
                    "edit_columns",
                    "filters",
                    "permissions",
                    "none"
                ]
            }
        }
    }
}
