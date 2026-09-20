__all__ = ["DriverConfigurationError", "DriverNotStartedError", "FrameworkError", "NetworkError"]


class FrameworkError(Exception):
    """Базовое исключение фреймворка."""


class DriverConfigurationError(FrameworkError):
    """Некорректные параметры драйвера: неизвестный ключ, тип или их комбинация."""


class DriverNotStartedError(FrameworkError):
    """Обращение к сессии до вызова start() или после quit()."""


class NetworkError(FrameworkError):
    """Не дождались запроса в ``NetworkLog.wait_for`` или упал колбэк маршрута."""
