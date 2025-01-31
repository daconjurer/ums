# Application exceptions (to handle within the application)

class CoreException(Exception):
    ...


class InvalidRoleException(CoreException):
    ...


class InvalidGroupException(CoreException):
    ...


class InvalidUserException(CoreException):
    ...


class AuthenticationException(CoreException):
    ...


class AuthorizationException(CoreException):
    ...
