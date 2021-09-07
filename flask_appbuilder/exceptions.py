class FABException(Exception):
    """Base FAB Exception"""

    ...


class InvalidColumnFilterFABException(FABException):
    """Invalid column for filter"""

    ...


class InvalidOperationFilterFABException(FABException):
    """Invalid operation for filter"""

    ...


class InvalidOrderByColumnFABException(FABException):
    """Invalid order by column"""

    ...


class InterfaceQueryWithoutSession(FABException):
    """You need to setup a session on the interface to perform queries"""

    ...


class PasswordComplexityValidationError(FABException):
    """Raise this when implementing your own password complexity function"""

    ...
