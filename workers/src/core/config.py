from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """TODO"""
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = ""
    postgres_user: str = ""
    postgres_password: str = ""

    rabbit_host: str = "localhost"
    rabbit_port: int = 5672
    rabbit_user: str = "guest"
    rabbit_password: str = "guest"

    class Config:
        env_file = '.env'
        extra = 'ignore'


settings = Settings()
