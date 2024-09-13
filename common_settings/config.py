import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """TODO"""
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = ""
    postgres_user: str = ""
    postgres_password: str = ""

    rabbit_host: str = os.environ.get('RABBIT_HOST')
    rabbit_port: int = 5672
    rabbit_user: str = "guest"
    rabbit_password: str = "guest"

    minio_host: str = os.environ.get('MINIO_HOST')
    minio_port: int = 9000
    minio_root_user: str = 'minio_user'
    minio_root_password: str = 'minio_password'
    minio_secure: bool = False
    minio_bucket_name: str = 'graduate-work-bucket'

    media_dir: str = 'media'

    debug_queue_message: bool = False

    class Config:
        env_file = '.env'
        extra = 'ignore'


settings = Settings()

