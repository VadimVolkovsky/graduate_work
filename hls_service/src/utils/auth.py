



# возможно использовать в для проверки роли или удалить



# import http
# from enum import StrEnum
# from typing import Annotated
#
# import jwt
# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
#
# from core.config import settings
# from models.auth import AccessTokenPayload, TokenType
#
# http_bearer_scheme = HTTPBearer()
#
#
# class RolesEnum(StrEnum):
#     SUBSCRIBER = "subscriber"
#     MANAGER = "manager"
#     SUPERUSER = "superuser"
#
#
# async def verify_access_token(
#     credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer_scheme)],
# ) -> AccessTokenPayload:
#     if not credentials:
#         raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail="Invalid authorization code.")
#     if not credentials.scheme == "Bearer":
#         raise HTTPException(
#             status_code=http.HTTPStatus.UNAUTHORIZED,
#             detail="Only Bearer token might be accepted",
#         )
#     token = credentials.credentials
#     try:
#         token_payload = jwt.decode(
#             token,
#             settings.auth.token_secret,
#             algorithms=[settings.auth.token_algorithm],
#             leeway=30,
#         )
#         access_token = AccessTokenPayload(**token_payload)
#     except jwt.exceptions.DecodeError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Access token is invalid or expired",
#         )
#     if access_token.type != TokenType.ACCESS:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token type",
#         )
#     return access_token
#
#
# class CheckRoles:
#     def __init__(self, from_token: list[str] | None = None) -> None:
#         self.from_token = from_token
#
#     async def __call__(
#         self,
#         access_token: AccessTokenPayload = Depends(verify_access_token),
#     ) -> bool:
#         if self.from_token:
#             if (
#                 not all([r in access_token.roles for r in self.from_token])
#                 and RolesEnum.SUPERUSER not in access_token.roles
#             ):
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="Not enough rights for this endpoint",
#                 )
#         return True
