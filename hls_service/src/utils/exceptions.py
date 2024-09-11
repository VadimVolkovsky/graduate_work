class GeneralError(Exception):
    """Базовая ошибка при работе с данными."""


class FileNotInStorage(GeneralError):
    """Нет плэйлиста в Minio"""


class MinioConnectionError(GeneralError):
    """Нет плэйлиста в Minio"""