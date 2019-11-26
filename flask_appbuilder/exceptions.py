class FABException(Exception):
    """Base FAB Exception"""
    pass


class InvalidColumnFilterFABException(FABException):
    """Invalid column for filter"""
    pass


class InvalidOperationFilterFABException(FABException):
    """Invalid operation for filter"""
    pass
