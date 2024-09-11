from sqlalchemy import create_engine, Column, String, UUID, DateTime
from sqlalchemy.orm import declarative_base
from workers.src.core.config import settings
# from core.config import settings

Base = declarative_base()


class Movie(Base):
    __tablename__ = 'Movie'

    id = Column(UUID, primary_key=True)
    title = Column(String(255))
    description = Column(String)
    video_file = Column(String)  # TODO Check
    hls_playlist_url = Column(String, nullable=True)
    upload_date = Column(DateTime)


if __name__ == '__main__':
    engine = create_engine(f"postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}@"
                           f"{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
