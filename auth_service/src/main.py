import logging
from contextlib import asynccontextmanager
from http import HTTPStatus

import uvicorn
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware

from redis.asyncio import Redis
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from api.v1.routers import main_router
from core.config import app_settings
from core.logger import LOGGING
from services import redis


# tracer = trace.get_tracer(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if app_settings.debug is True:
        # await purge_database()  # TODO использовать алембик
        # await create_database()  # TODO использовать алембик
        # await add_default_roles()
        pass

    # if app_settings.jaeger.enable_tracer:
    #     configure_tracer(
    #         app_settings.jaeger.jaeger_host,
    #         app_settings.jaeger.jaeger_port,
    #         app_settings.project_name,
    #     )

    redis.redis = Redis(host=app_settings.redis_host, port=app_settings.redis_port)
    await FastAPILimiter.init(redis.redis)
    yield
    await redis.redis.close()
    await FastAPILimiter.close()


app = FastAPI(
    title=app_settings.project_name,
    description="Сервис авторизации",
    version="1.0.0",
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

# Google OAuth 2.0 settings
app.add_middleware(SessionMiddleware, secret_key="secret")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router, prefix='/api/v1')
add_pagination(app)





# TODO подумать куда вынести
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=HTTPStatus.UNAUTHORIZED,
        content={"detail": exc.message}
    )


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_settings.service_host,
        port=app_settings.service_port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
