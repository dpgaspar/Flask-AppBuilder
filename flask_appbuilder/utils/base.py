def get_column_root_relation(column: str) -> str:
    if "." in column:
        return column.split(".")[0]
    return column


def get_column_leaf(column: str) -> str:
    if "." in column:
        return column.split(".")[1]
    return column


def is_column_dotted(column: str) -> bool:
    return "." in column
