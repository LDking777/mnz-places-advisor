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


class UpstreamTimeoutError(ServiceError):
    status_code = 504
    code = "upstream_timeout"
    default_message = "El proveedor de lugares no respondió a tiempo."


class UpstreamServiceError(ServiceError):
    status_code = 502
    code = "upstream_error"
    default_message = "El proveedor de lugares devolvió una respuesta no válida."


class InvalidUpstreamResponse(ServiceError):
    status_code = 502
    code = "invalid_upstream_payload"
    default_message = "El proveedor de lugares devolvió un payload con un formato inesperado."
