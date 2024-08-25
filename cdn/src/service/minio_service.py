from minio import Minio
from minio.error import S3Error


class MinioService:
    """Сервис для работы с CDN Minio"""

    def __init__(self):
        self.bucket_name = "volkovskiy-test-bucket-33"
        self.client = Minio(
            "play.min.io",
            access_key="Q3AM3UQ867SPQQA43P2F",
            secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
        )

    def upload_files(self, file_dir: str, filenames: list):
        """
        Загрузка файлов в CDN Minio
        :param file_dir: путь до директории с файлами для загрузки: 'path/to/dir'
        :param filenames: список с названиями файлов в директории: ['new_film_480p.m3u8', 'new_film_720p.m3u8', ...]
        """
        try:
            self._check_bucket_exists()

            for object_name in filenames:
                file_path = f"{file_dir}/{object_name}"
                self.client.fput_object(
                    self.bucket_name,
                    object_name,
                    file_path,
                )
                print(f'{object_name} успешно загружен в корзину {self.bucket_name}')
        except S3Error as exc:
            print(f"Произошла ошибка {exc}")

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
