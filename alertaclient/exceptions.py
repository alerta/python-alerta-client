
try:
    from click import ClickException as ClientException
except:
    class ClientException(Exception):
        pass


class AlertaException(ClientException):
    pass


class ConfigurationError(AlertaException):
    pass


class AuthError(AlertaException):
    pass


class ApiError(AlertaException):
    pass


class UnknownError(AlertaException):
    pass
