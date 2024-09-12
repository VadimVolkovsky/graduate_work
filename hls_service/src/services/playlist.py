import logging
from functools import lru_cache
from urllib3.exceptions import MaxRetryError, NewConnectionError

from cdn.src.minio_service import MinioService
from utils.exceptions import FileNotInStorage, MinioConnectionError
from core.config import settings

logger = logging.getLogger(__name__)

class PlaylistService:
    """Класс для работы с плэйлистами m3u8."""

    def __init__(self, storage: MinioService, nginx_host, nginx_port):
        self.host = nginx_host
        self.port = nginx_port
        self.storage = storage

    def get_playlist_url(self, film_id: str):
        files = self.storage.get_list_of_all_files(film_id)
        bucket_name = self.storage.bucket_name
        try:
            file = [f.object_name for f in files if f.object_name.endswith('m3u8')]
        except (MaxRetryError, NewConnectionError):
            logger.exception(f"Fail request to Minio")
            raise MinioConnectionError

        if not file:
            logger.exception(f"Fail request to get playlist for {film_id=}")
            raise FileNotInStorage
        file_name = file[0]

        return f'http://{self.host}:{self.port}/hls/videos/{bucket_name}/{file_name}'


@lru_cache()
def get_playlist_service() -> PlaylistService:
    return PlaylistService(
        MinioService(), settings.nginx_host, settings.nginx_port
    )
