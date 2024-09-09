import os

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AuthBaseSettings(BaseSettings):
    class Config:
        env_file = '.env'
        extra = 'ignore'


# class JaegerSettings(AuthBaseSettings):
#     jaeger_host: str = Field(
#         default='jaeger_service',
#     )
#     jaeger_port: int = Field(
#         default=6831,
#     )
#     enable_tracer: bool = Field(default=True)


class AppSettings(AuthBaseSettings):
    project_name: str = Field(default='auth')

    service_host: str
    service_port: int
    service_url: str

    auth_postgres_host: str
    auth_postgres_port: int
    auth_postgres_db: str
    auth_postgres_user: str
    auth_postgres_password: str
    echo: bool = False  # вывод операций с БД в логи

    redis_host: str
    redis_port: int

    authjwt_secret_key: str = "secret"
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}
    access_expires: int = 3600
    refresh_expires: int = 86400

    # google OAuth 2.0 settings
    redirect_url: str
    client_id: str
    client_secret: str

    debug: bool = Field(default='False')

    # jaeger: JaegerSettings = JaegerSettings()

    @property
    def database_url(self):
        return (f'postgresql+asyncpg://{self.auth_postgres_user}:{self.auth_postgres_password}@'
                f'{self.auth_postgres_host}:{self.auth_postgres_port}/{self.auth_postgres_db}')


app_settings = AppSettings()
