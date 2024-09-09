import json
import os
from datetime import timedelta

from minio import Minio
from minio.error import S3Error

from core.config import settings


class MinioService:
    """Сервис для работы с Minio"""

    def __init__(
            self,
            bucket_name=settings.minio_bucket_name,
            media_dir=settings.media_dir
    ):
        self.bucket_name = bucket_name
        self.media_dir = media_dir
        self.client = Minio(
            endpoint=f"{settings.minio_host}:{settings.minio_port}",
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            secure=settings.minio_secure
        )

    def upload_files(self, film_id: str, file_dir: str):
        """
        Загружает в Minio все файлы из указанной директории.
        Подойдет для загрузки видеофайлов после конвертации в формат m3u8.
        :param file_dir: путь до директории с файлами для загрузки: 'path/to/dir'
        """
        try:
            self._check_bucket_exists()
            filenames = os.listdir(file_dir)

            for filename in filenames:
                remote_filepath = f"{film_id}/{filename}"  # путь до файла в корзине
                local_filepath = f"{file_dir}/{filename}"  # путь до файла локально
                print(f'Загрузка файла {filename}...')
                result = self.client.fput_object(self.bucket_name, object_name=remote_filepath, file_path=local_filepath)
                print(f'{result.object_name} успешно загружен в корзину {result.bucket_name}')
        except S3Error as exc:
            print(f"Произошла ошибка {exc}")

    def upload_file(self, film_id: str, filename: str) -> str:
        """
        Загрузка файла в Minio
        Файлы должны находится в директории self.media_dir - по умолчанию это папка /media
        :param film_id: <'cc733c92-6853-45f6-8e49-bec741188ebb'>
        :param filename: <'short_video.mp4'>
        :return remote_filepath: <film_id>/<filename>
        """
        remote_filepath = f"{film_id}/{filename}"  # путь до файла в корзине
        local_filepath = f'{self.media_dir}/{film_id}/{filename}'  # путь до файла локально
        try:
            self._check_bucket_exists()
            print(f'Загрузка файла {filename}...')
            result = self.client.fput_object(self.bucket_name, object_name=remote_filepath, file_path=local_filepath)
            print(f'{result.object_name} успешно загружен в корзину {result.bucket_name}')
            return remote_filepath
        except S3Error as exc:
            print(f"Произошла ошибка {exc}")

    def get_presigned_url(self, filename) -> str:
        """
        Создание presigned_url на загруженный в Minio файл.
        По данному url можно скачать видеофайл из Minio.
        """
        url = self.client.presigned_get_object(
            self.bucket_name, filename, expires=timedelta(hours=12),
        )
        print(url)
        return url

    def get_file_url(self, remote_filepath): # TODO доработать
        file_url = f"http://minio:9001/api/v1/buckets/graduate-work-bucket/objects/download?prefix={remote_filepath}"
        return file_url


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

    def get_list_of_all_files(self, prefix):
        """Возвращает список всех файлов в корзине"""
        objects = self.client.list_objects(self.bucket_name, prefix=f"{prefix}/")
        # print(f'Список файлов в корзине {self.bucket_name}:')
        # for obj in objects:
        #     print(obj.object_name)
        return objects


    def set_up_policy(self):
        """расширение политики минио чтобы можно было скачивать файлы без авторизации"""
        # Example anonymous read-write bucket policy.
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": [
                        "s3:GetBucketLocation",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                    ],
                    "Resource": "arn:aws:s3:::graduate-work-bucket",
                },
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:ListMultipartUploadParts",
                        "s3:AbortMultipartUpload",
                    ],
                    "Resource": "arn:aws:s3:::graduate-work-bucket/*",
                },
            ],
        }
        self.client.set_bucket_policy("graduate-work-bucket", json.dumps(policy))


### TODO для отладки - загрузка тестового видеофайла из папки /media в минио
if __name__ == '__main__':
    filename = 'SampleVideo_1280x720_10mb.mp4'
    minio_service = MinioService()
    minio_service.upload_file(filename)
    minio_service.get_presigned_url(filename)
#     minio_service.set_up_policy()
