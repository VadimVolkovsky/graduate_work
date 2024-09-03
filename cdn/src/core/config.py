from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """TODO"""
    minio_host: str = 'localhost'
    minio_port: int = 9000
    minio_root_user: str = 'minio_user'
    minio_root_password: str = 'minio_password'
    minio_secure: bool = False
    minio_bucket_name: str = 'graduate-work-bucket'

    media_dir: str = './media'

    class Config:
        extra = 'ignore'


settings = Settings()
