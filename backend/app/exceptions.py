class ServiceError(Exception):
    status_code = 500
    code = "internal_error"
    default_message = "Ocurrió un error inesperado."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class ConfigurationError(ServiceError):
    status_code = 503
    code = "configuration_error"
    default_message = "El servicio no tiene una configuración válida."


class DatabaseUnavailableError(ServiceError):
    status_code = 503
    code = "database_unavailable"
    default_message = "La base de datos de lugares no está disponible."


class UpstreamTimeoutError(ServiceError):
    status_code = 504
    code = "upstream_timeout"
    default_message = "El servicio externo no respondió a tiempo."


class UpstreamServiceError(ServiceError):
    status_code = 502
    code = "upstream_error"
    default_message = "El servicio externo devolvió una respuesta no válida."
