from typing import Optional


class FABException(Exception):
    """Base FAB Exception"""

    def __init__(self, *args, exception: Optional[Exception] = None) -> None:
        self.exception = exception
        super().__init__(*args)

    def __str__(self):
        return (
            f"{self.__class__.__name__}: {self.exception.__class__.__name__}"
            if self.exception
            else super().__str__()
        )


class DatabaseException(FABException):
    """Database related exception"""


class InvalidColumnFilterFABException(FABException):
    """Invalid column for filter"""

    ...


class InvalidOperationFilterFABException(FABException):
    """Invalid operation for filter"""

    ...


class InvalidOrderByColumnFABException(FABException):
    """Invalid order by column"""

    ...


class PasswordComplexityValidationError(FABException):
    """Raise this when implementing your own password complexity function"""

    ...


class ApplyFilterException(FABException):
    """When executing an apply filter a SQLAlchemy exception happens"""

    ...


class OAuthProviderUnknown(FABException):
    """
    When an OAuth provider is not supported/unknown
    """

    ...


class InvalidLoginAttempt(FABException):
    """
    When the credentials entered could not be verified
    """

    ...


class DeleteGroupWithUsersException(FABException):
    """
    When trying to delete a group with users
    """


class DeleteRoleWithUsersException(FABException):
    """
    When trying to delete a role with users
    """
