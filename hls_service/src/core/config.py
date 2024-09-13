from logging import config as logging_config

from core.logger import LOGGING
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

logging_config.dictConfig(LOGGING)


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    """Главный класс настроек всего приложения"""

    minio_host: str = 'localhost'
    minio_port: int = 9000
    minio_root_user: str = 'minio_user'
    minio_root_password: str = 'minio_password'
    minio_secure: bool = False
    minio_bucket_name: str = 'graduate-work-bucket'
    media_dir: str = 'media'

    movie_api_project_name: str = "hls_api"
    movie_api_app_port: int = 8002
    nginx_host: str = "127.0.0.1"
    nginx_port: int = 80


    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )


settings = Settings()
