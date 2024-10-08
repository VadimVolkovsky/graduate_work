import datetime
from http import HTTPStatus
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from authlib.integrations.base_client.errors import OAuthError
from core.schemas.entity import (UserInDB, AdminInDB, UserCreate, UserLogin, JWTResponse, UserUpdate,
                                 UserLoginHistoryInDB)
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi_limiter.depends import RateLimiter
from fastapi_pagination import Page, paginate
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from core.config import AppSettings, app_settings
from db.postgres import get_session
from helperes.google_auth import oauth
from models.entity import SocialNetworksEnum
from services import redis
from services.user_service import get_user_service, UserService

from helperes.auth import roles_required
from helperes.auth_request import AuthRequest
from models.entity import Roles

router = APIRouter()
auth_dep = AuthJWTBearer()


@AuthJWT.load_config
def get_config():
    return AppSettings()


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti']
    entry = await redis.redis.get(jti)

    if entry:
        entry = entry.decode()

    return entry and entry == 'true'


@router.post(
    '/signup',
    response_model=UserInDB,
    status_code=HTTPStatus.CREATED,
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def create_user(
        user_create: UserCreate,
        user_service: UserService = Depends(get_user_service),
        session: AsyncSession = Depends(get_session)
) -> UserInDB:
    """Эндпоинт создания нового пользователя"""
    return await user_service.create_user(user_create, session)


@router.post(
    '/login',
    response_model=JWTResponse,
    status_code=HTTPStatus.OK,
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def login(
        user: UserLogin,
        user_service: UserService = Depends(get_user_service),
        authorize: AuthJWT = Depends(auth_dep),
        session: AsyncSession = Depends(get_session)
):
    """
    Эндпоинт авторизации пользователя по логину и паролю.
    В случае успешной авторизации создаются access и refresh токены
    """
    if not await user_service.check_user_credentials(user.email, user.password, session):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Bad email or password")

    access_token = await authorize.create_access_token(
        subject=user.email)  # TODO заменить на метод create_jwt_tokens из user_service
    raw_jwt = await authorize.get_raw_jwt(encoded_token=access_token)
    access_token_jti = raw_jwt['jti']

    refresh_token = await authorize.create_refresh_token(
        subject=user.email,
        user_claims={'access_token_jti': access_token_jti}
    )

    await user_service.add_user_login_history(user.email, 'auth', session)

    return JWTResponse(access_token=access_token, refresh_token=refresh_token)


@router.post(
    '/login_admin',
    response_model=AdminInDB,
    status_code=HTTPStatus.OK,
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def login_admin(
        user: UserLogin,
        user_service: UserService = Depends(get_user_service),
        authorize: AuthJWT = Depends(auth_dep),
        session: AsyncSession = Depends(get_session)
):
    """
    Эндпоинт входа в админку по логину и паролю.
    В случае успешной авторизации возвращаются данные пользователя
    """
    if not await user_service.check_user_credentials(user.email, user.password, session):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Bad email or password")

    user_from_db = await user_service.get_user_by_email(user.email, session)

    if user_from_db.role.name != 'admin':
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Only admin can access this URL')

    await user_service.add_user_login_history(user.email, 'site', session)

    return AdminInDB(
        id=user_from_db.id,
        first_name=user_from_db.first_name,
        last_name=user_from_db.last_name,
        email=user_from_db.email,
        role=user_from_db.role.name,
    )


@router.get('/check_film_access/', status_code=HTTPStatus.OK)
@roles_required(roles_list=[Roles.subscriber.value, Roles.superuser.value])
async def check_film_access(
        request: AuthRequest,
        authorize: AuthJWT = Depends(auth_dep),
):
    """Эндпоинт проверки доступности пользователю фильма"""
    await authorize.jwt_required()
    raw_jwt = await authorize.get_raw_jwt()

    token_expire_date = raw_jwt["exp"]
    time_now = datetime.datetime.utcnow().timestamp()

    if time_now >= token_expire_date:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Token expired")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post('/check_token', status_code=HTTPStatus.OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))], )
async def check_token(
        user_service: UserService = Depends(get_user_service),
        authorize: AuthJWT = Depends(auth_dep),
        session: AsyncSession = Depends(get_session)
):
    """
    Эндпоинт для проверки актуальности токена.
    Если у токена истек срок жизни, возвращаем код 403
    Если токен валиден, возвращаем в ответе данные пользователя из БД
    """
    await authorize.jwt_required()
    raw_jwt = await authorize.get_raw_jwt()
    token_expire_date = raw_jwt["exp"]
    time_now = datetime.datetime.utcnow().timestamp()

    if time_now >= token_expire_date:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Token expired")

    email = raw_jwt['sub']
    user = await user_service.get_user_by_email(email, session)

    return {'email': user.email, 'role': user.role.name}


@router.delete('/logout', status_code=HTTPStatus.OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))], )
async def logout(
        user_service: UserService = Depends(get_user_service),
        authorize: AuthJWT = Depends(auth_dep),
):
    """Эндпоинт разлогинивания пользователя путем добавления его refresh и access токенов в блэк-лист Redis"""
    await authorize.jwt_refresh_token_required()
    raw_jwt = await authorize.get_raw_jwt()
    refresh_token_jti = raw_jwt['jti']
    access_token_jti = raw_jwt['access_token_jti']
    await user_service.redis.setex(refresh_token_jti, app_settings.refresh_expires, 'true')
    await user_service.redis.setex(access_token_jti, app_settings.access_expires, 'true')
    return {"detail": "Logged out successfully"}


@router.post('/refresh', dependencies=[Depends(RateLimiter(times=2, seconds=5))], )
async def refresh(authorize: AuthJWT = Depends(auth_dep)):
    """
    Эндпоинт получения нового access токена по refresh токену.
    В случае если refresh токен в блэк-листе Redis, новый access токен не выдается
    """
    await authorize.jwt_refresh_token_required()
    current_user = await authorize.get_jwt_subject()
    new_access_token = await authorize.create_access_token(subject=current_user)
    return {"access_token": new_access_token}


@router.post('/user_update', status_code=HTTPStatus.OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))],)
async def change_user_data(
        user_input_data: UserUpdate,
        authorize: AuthJWT = Depends(auth_dep),
        user_service: UserService = Depends(get_user_service),
        session: AsyncSession = Depends(get_session)
):
    """Эндпоинт для обновления данных пользователя"""
    await authorize.jwt_required()
    raw_jwt = await authorize.get_raw_jwt()
    email = raw_jwt['sub']
    await user_service.update_user_info(user_input_data, email, session)
    jti = raw_jwt['jti']
    await user_service.redis.setex(jti, app_settings.refresh_expires, 'true')
    return {"detail": "Data were updated successfully"}


@router.get(
    '/user_login_history',
    response_model=Page[UserLoginHistoryInDB],
    status_code=HTTPStatus.OK,
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def get_user_login_history(
        authorize: AuthJWT = Depends(auth_dep),
        user_service: UserService = Depends(get_user_service),
        session: AsyncSession = Depends(get_session)
):
    """Эндпоинт для получения информации об истории входов пользователя"""
    await authorize.jwt_required()
    email = await authorize.get_jwt_subject()
    user = await user_service.get_user_by_email(email, session)
    user_login_history = await user_service.get_user_login_history(user, session)
    return paginate(user_login_history)


@router.get("/login_social_network", dependencies=[Depends(RateLimiter(times=2, seconds=5))], )
async def login_social_network(
        request: Request,
        social_network: str
):
    """Эндпоинт для авторизации через социальные сети"""
    redirect_url = app_settings.redirect_url

    if social_network == 'google':
        return await oauth.google.authorize_redirect(request, redirect_url)
    else:
        raise HTTPException(detail=f'Авторизация через {social_network} пока не реализована')


@router.get(
    "/social_network_auth",
    response_model=JWTResponse,
    status_code=HTTPStatus.OK,
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def social_network_auth(
        request: Request,
        authorize: AuthJWT = Depends(auth_dep),
        user_service: UserService = Depends(get_user_service),
        session: AsyncSession = Depends(get_session),
):
    """Redirect URL для авторизации через социальные сети"""
    try:
        for request_session in request.session.keys():  # TODO есть ли другие варианты проверки источника запроса?
            if SocialNetworksEnum.GOOGLE.value in request_session:
                token = await oauth.google.authorize_access_token(request)
                social_network = SocialNetworksEnum.GOOGLE.value
                break
        else:
            raise HTTPException(detail='Авторизация через другие соц.сети пока не поддерживается')
    except OAuthError as error:
        raise Exception(error)

    user = token.get('userinfo')

    if user:
        request.session['user'] = dict(user)

    return await user_service.login_user_with_social_network(session, user, social_network, authorize)
