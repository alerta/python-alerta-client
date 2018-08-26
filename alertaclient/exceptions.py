
try:
    from click import ClickException as ClientException  # type: ignore
except:
    class ClientException(Exception):  # type: ignore
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
