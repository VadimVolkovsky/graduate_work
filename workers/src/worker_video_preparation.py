import os
import shutil
import tempfile
from functools import lru_cache

import ffmpeg

from cdn.src.minio_service import MinioService
from common_settings.logger import logger


class WorkerVideoPreparation:
    """
    Воркер для обработки и добавления новых видеофайлов в Minio.
    Воркер получает из очереди сообщения о новых видеофайлах,
    запускает процесс конвертации загруженного в Minio видеофайла в формат m3u8,
    загружает подготовленные m3u8 файлы в Minio.
    """

    def __init__(self, film_id: str = None, file_url: str = None, file_name: str = None):
        self.film_id = film_id
        self.file_url = file_url
        self.file_name = file_name
        self._local_file_path: str | None = None
        self.minio_service = MinioService()

    def convert_video(self):
        """Конвертирует видео в m3u8 формат и сохраняет в временную директорию."""
        self._local_file_path = tempfile.mkdtemp()

        logger.info(f'Создана временная директория для конвертации: {self._local_file_path}')

        filename_without_format = self.file_name.split('/')[-1].split('.')[0]
        output_path_to_file = f'{self._local_file_path}/{filename_without_format}.m3u8'

        input_stream = ffmpeg.input(self.file_url)
        output_stream = ffmpeg.output(
            input_stream,
            output_path_to_file,
            format='hls',
            start_number=0,
            hls_time=5,
            hls_list_size=0
        )

        logger.info(f'Запускаем конвертацию {self.file_name}...')
        ffmpeg.run(output_stream)
        logger.info(f'Конвертация завершена {self.file_name}. Файлы сохранены во временной директории {self._local_file_path}')

    async def upload_files_in_minio(self):
        """Загрузка сконвертированных файлов в Minio из временной директории"""
        logger.info(f'Загружаем файлы из временной директории {self._local_file_path} в Minio')

        self.minio_service.upload_files(film_id=self.film_id, file_dir=self._local_file_path)

        logger.info(f'Удаление временных файлов...')
        shutil.rmtree(self._local_file_path, ignore_errors=True)
        logger.info(f'Временные файлы удалены.')

@lru_cache()
def get_worker() -> WorkerVideoPreparation:
    return WorkerVideoPreparation()
