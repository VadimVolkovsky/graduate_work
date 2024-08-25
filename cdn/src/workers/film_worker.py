from service.minio_service import MinioService
from service.video_converter_service import VideoConverterService


class FilmWorker:
    """Воркер для работы с фильмами"""
    def __init__(self):
        self.video_converter_service = VideoConverterService()
        self.minio_service = MinioService()

    def load_new_film(self, filename: str):
        """
        Метод для добавления нового фильма в хранилище CDN Minio
        :param filename: название файла с форматом - 'new_film.mp4'
        """
        file_dir, filenames = self.video_converter_service.convert_to_hls(filename)
        self.minio_service.upload_files(file_dir, filenames)
