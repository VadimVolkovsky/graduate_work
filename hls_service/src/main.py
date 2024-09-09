import logging
import uvicorn
from api.v1 import films
from core.config import settings
from core.logger import LOGGING
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse


app = FastAPI(
    title=settings.movie_api_project_name,
    docs_url="/api/openapi",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

app.include_router(films.router, prefix="/api/v1/films", tags=["films"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=settings.movie_api_app_port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
