import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Cхема UserCreate описывает то, что мы ожидаем получить при создании записи в базе данных. """
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserLogin(BaseModel):
    """Модель для работы с аутентификацией пользователя"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Модель обновления данных пользователя"""
    email: EmailStr | None = None
    password: str | None = None


class UserInDB(BaseModel):
    """UserInDB — это то, что мы будем отдавать пользователю — детальную информацию по нужным полям модели. """
    id: UUID
    first_name: str
    last_name: str

    class Config:
        orm_mode = True
        from_attributes = True


class AdminInDB(UserInDB):
    """AdminInDB — это то, что мы будем отдавать для входа в админку — детальную информацию по нужным полям модели. """
    email: EmailStr
    role: str

    class Config:
        orm_mode = True
        from_attributes = True


class UserLoginHistory(BaseModel):
    user_id: UUID
    user_auth_service: str


class UserLoginHistoryInDB(BaseModel):
    """
    UserLoginHistoryInDB — это то, что мы будем отдавать пользователю — детальную информацию по нужным полям модели.
    """
    login_date: datetime.datetime


class UserSocialNetwork(BaseModel):
    user_id: UUID
    social_network_id: int


class JWTResponse(BaseModel):
    """Модель для работы с токенами"""
    access_token: str
    refresh_token: str
