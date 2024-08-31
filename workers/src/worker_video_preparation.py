import os
from functools import lru_cache

import ffmpeg

from cdn.src.minio_service import MinioService
# from minio_service import MinioService


class WorkerVideoPreparation:
    """
    Воркер для обработки и добавления новых видеофайлов в Minio.
    Воркер получает из очереди сообщения о новых видеофайлах,
    запускает процесс конвертации загруженного в Minio видеофайла в формат m3u8,
    загружает подготовленные m3u8 файлы в Minio.
    """

    def __init__(self, file_url: str = None, file_name: str = None):
        self.file_url = file_url
        self.file_name = file_name
        self._local_file_path: str | None = None
        self.minio_service = MinioService()

    def convert_video(self):
        """Конвертирует видео в m3u8 формат"""
        input_stream = ffmpeg.input(self.file_url)
        filename_without_format = self.file_name.split('.')[0]
        converted_video_dir = f'{os.getcwd()}/media/{filename_without_format}'
        print('Создаем директорию для конвертации фильма...')
        os.makedirs(converted_video_dir, exist_ok=True)
        output_filename = f'{filename_without_format}.m3u8'
        output_path_to_file = f'{converted_video_dir}/{output_filename}'
        output_stream = ffmpeg.output(
            input_stream,
            output_path_to_file,
            format='hls',
            start_number=0,
            hls_time=5,
            hls_list_size=0
        )

        print('Запускаем конвертацию...')
        ffmpeg.run(output_stream)

        self._local_file_path = converted_video_dir

    async def upload_files_in_minio(self):
        """Загрузка сконвертированных файлов в Minio"""
        self.minio_service.upload_files(self._local_file_path)


@lru_cache()
def get_worker() -> WorkerVideoPreparation:
    return WorkerVideoPreparation()
