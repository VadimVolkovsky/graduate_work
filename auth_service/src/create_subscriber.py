import typer
from sqlalchemy import create_engine, select
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import app_settings
from models.entity import User, Role

Base = declarative_base()
dsn = (f'postgresql+psycopg2://{app_settings.auth_postgres_user}:{app_settings.auth_postgres_password}@'
       f'{app_settings.auth_postgres_host}:{app_settings.auth_postgres_port}/{app_settings.auth_postgres_db}')
engine = create_engine(dsn, echo=True, future=True)
session_maker = sessionmaker(engine, expire_on_commit=False)
session = session_maker()


def create_subscriber():
    """Создание супер пользователя"""
    role_obj = session.execute(select(Role).where(Role.name == 'subscriber'))
    admin_role = role_obj.scalars().first()

    user_obj = User(
        email='user@mail.ru',
        first_name='user',
        last_name='god',
        password='user',
        role=admin_role
    )

    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)

    print('subscriber created:')
    print(f'email: {user_obj.email}')
    print('password: user')


if __name__ == "__main__":
    typer.run(create_subscriber)
