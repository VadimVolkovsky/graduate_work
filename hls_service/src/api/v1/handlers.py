from typing import Callable
from fastapi import HTTPException, status, Request, Response
from fastapi.routing import APIRoute

from utils import exceptions


class ExceptionHandlerRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except exceptions.FileNotInStorage:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="The wrong film_id. Film not exist.",
                )
            except exceptions.MinioConnectionError:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal error.",
                )

        return custom_route_handler
