__all__ = ["DriverConfigurationError", "DriverNotStartedError", "FrameworkError", "NetworkError"]


class FrameworkError(Exception):
    """Base error for the framework."""


class DriverConfigurationError(FrameworkError):
    """The driver config has an unknown field, a bad type, or an invalid combination."""


class DriverNotStartedError(FrameworkError):
    """The session was used before start or after quit."""


class NetworkError(FrameworkError):
    """A waited-for request never arrived, or a route callback failed."""
