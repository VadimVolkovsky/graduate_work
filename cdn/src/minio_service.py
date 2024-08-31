import os
from datetime import timedelta

from minio import Minio
from minio.error import S3Error


class MinioService:
    """Сервис для работы с Minio"""

    def __init__(
            self,
            bucket_name="volkovskiy-test-bucket-33",  # TODO env
            media_dir='./media'   # TODO env
    ):
        self.bucket_name = bucket_name
        self.media_dir = media_dir
        self.client = Minio(
            "play.min.io",
            access_key="Q3AM3UQ867SPQQA43P2F",
            secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
        )  # TODO заменить на локальный запуск Minio
           # TODO env

    def upload_files(self, file_dir: str):
        """
        Загружает в Minio все файлы из указанной директории.
        Подойдет для загрузки видеофайлов после конвертации в формат m3u8.
        :param file_dir: путь до директории с файлами для загрузки: 'path/to/dir'
        """
        try:
            self._check_bucket_exists()
            filenames = os.listdir(file_dir)

            for filename in filenames:
                filepath = f"{file_dir}/{filename}"
                print(f'Загрузка файла {filename}...')
                result = self.client.fput_object(self.bucket_name, filename, filepath)
                print(f'{result.object_name} успешно загружен в корзину {result.bucket_name}')
        except S3Error as exc:
            print(f"Произошла ошибка {exc}")

    def upload_file(self, filename: str):
        """
        Загрузка файла в Minio
        Файлы должны находится в директории self.media_dir - по умолчанию это папка /media
        :param filename: пример 'short_video.mp4'
        """
        filepath = f'{self.media_dir}/{filename}'
        try:
            self._check_bucket_exists()
            print(f'Загрузка файла {filename}...')
            result = self.client.fput_object(self.bucket_name, filename, filepath)
            print(f'{result.object_name} успешно загружен в корзину {result.bucket_name}')
        except S3Error as exc:
            print(f"Произошла ошибка {exc}")

    def get_presigned_url(self, filename):
        """
        Создание presigned_url на загруженный в Minio файл.
        По данному url можно скачать видеофайл из Minio.
        """
        url = self.client.presigned_get_object(
            self.bucket_name, filename, expires=timedelta(hours=12),
        )
        print(url)

    def _check_bucket_exists(self):
        """
        Метод проверяет существование необходимой корзины в Minio и
        создает ее при необходимости.
        """
        found = self.client.bucket_exists(self.bucket_name)
        if not found:
            self.client.make_bucket(self.bucket_name)
            print(f"Создана корзина {self.bucket_name}")
        else:
            print(f"Корзина {self.bucket_name} уже существует")

    def get_list_of_all_files(self):
        """Возвращает список всех файлов в корзине"""
        objects = self.client.list_objects(self.bucket_name)
        print(f'Список файлов в корзине {self.bucket_name}:')
        for obj in objects:
            print(obj.object_name)


### TODO для отладки - загрузка тестового видеофайла из папки /media в минио
if __name__ == '__main__':
    filename = 'SampleVideo_1280x720_10mb.mp4'
    minio_service = MinioService()
    minio_service.upload_file(filename)
    minio_service.get_presigned_url(filename)
