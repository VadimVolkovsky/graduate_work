import contextlib
import datetime
import uuid
from enum import Enum

from sqlalchemy import String, ForeignKey, UniqueConstraint, Text, Column, DateTime, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import get_session

from db.postgres import Base


class Roles(Enum):
    user: str = 'user'
    superuser: str = 'superuser'
    admin: str = 'admin'
    subscriber: str = 'subscriber'


class SocialNetworksEnum(Enum):
    GOOGLE: str = 'google'
    YANDEX: str = 'yandex'
    VK: str = 'vk'


# получение DI через контекстный менеджер
get_async_session_context = contextlib.asynccontextmanager(get_session)


async def add_default_roles():
    """Добавляет роли в БД при старте приложения"""
    async with get_async_session_context() as db_session:
        for role in Roles:
            role_obj = Role(name=role.value)
            db_session.add(role_obj)
            await db_session.commit()


class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(20))

    def __init__(self, name: str) -> None:
        self.name = name


class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    # TODO заменить datetime на актуальный аналог
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)
    role_id: Mapped[Role] = mapped_column(ForeignKey('roles.id'), default=1)
    role = relationship("Role", lazy="selectin")
    login_history = relationship('UserLoginHistory', back_populates='user', passive_deletes=True)

    def __init__(self, email: str, password: str, first_name: str, last_name: str, role: int = None) -> None:
        self.email = email
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.role = role

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.email}>'


def create_partition(target, connection, **kw):
    """ Создает партицирование в модели user_history.
        Не создается в автоматических миграциях,
        необходимо дописывать руками migrations/versions,
        перед выполнением команды flask db upgrade
     """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_login_history_site"
        PARTITION OF "user_login_history" FOR VALUES IN ('site')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_login_history_social"
        PARTITION OF "user_login_history" FOR VALUES IN ('social')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_login_history_auth"
        PARTITION OF "user_login_history" FOR VALUES IN ('auth')"""
    )


class UserLoginHistory(Base):
    __tablename__ = 'user_login_history'
    __table_args__ = (
        UniqueConstraint('id', 'user_auth_service'),  # Включаем user_auth_service в уникальное ограничение
        {
            'postgresql_partition_by': 'LIST (user_auth_service)',
            'listeners': [('after_create', create_partition)],
        }
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[User] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'),
                                          nullable=False)
    user = relationship('User', back_populates='login_history')
    user_auth_service = Column(Text, primary_key=True, nullable=False)
    login_date: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<UserLoginHistory {self.user_id}:{self.login_date}:{self.user_auth_service}>'

    def __init__(self, user_id: User, user_auth_service: str) -> None:
        self.user_id = user_id
        self.user_auth_service = user_auth_service


class SocialNetwork(Base):
    __tablename__ = 'social_networks'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(20))

    def __init__(self, name: str) -> None:
        self.name = name


class UserSocialNetworks(Base):
    __tablename__ = 'user_social_networks'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id: Mapped[User] = mapped_column(ForeignKey('users.id'), nullable=False)
    user = relationship('User')
    social_network_id: Mapped[SocialNetwork] = mapped_column(ForeignKey('social_networks.id'), nullable=False)
    social_network = relationship("SocialNetwork", lazy="selectin")

