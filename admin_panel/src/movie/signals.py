import json
import logging

import pika
from django.db.models.signals import post_save
from django.dispatch import receiver

from config import settings
from .models import Movie
from django.core.files.storage import default_storage
from django.db import transaction
from tasks import task_send_message_to_rabbitmq

logger = logging.getLogger(__name__)


# MAX_RETRIES = 5  # Максимальное количество попыток
# RETRY_DELAY = 10  # Задержка между попытками в секундах
#
#
# @shared_task(bind=True, max_retries=MAX_RETRIES)
# def check_file_in_storage_task(self, movie_id, file_name):
#     """Периодическая задача для проверки доступности файла в хранилище."""
#     try:
#         if default_storage.exists(file_name):
#             print(f"Файл {file_name} доступен в хранилище.")
#
#             # Отправка сообщения в RabbitMQ о завершении загрузки файла
#             movie = Movie.objects.get(id=movie_id)
#             send_message_to_rabbitmq(movie_id, file_name, movie.video_file.url)
#         else:
#             print(f"Файл {file_name} недоступен, повторная проверка через {RETRY_DELAY} секунд...")
#             raise self.retry(countdown=RETRY_DELAY)  # Повторная попытка через RETRY_DELAY секунд
#     except Exception as e:
#         print(f"Произошла ошибка: {e}")
#         raise self.retry(exc=e)  # Если ошибка, продолжаем повторять задачу


# def send_message_to_rabbitmq(film_id, file_name, file_url):
#     connection = pika.BlockingConnection(pika.ConnectionParameters(
#         host=settings.RABBITMQ_HOST,
#         port=settings.RABBITMQ_PORT,
#         credentials=pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
#     ))
#     channel = connection.channel()
#
#     # Объявляем очередь, если она еще не создана
#     channel.queue_declare(queue='new_video')
#
#     message = {
#         "film_id": str(film_id),
#         "file_name": file_name,
#         "url_original_video": file_url
#     }
#
#     # Отправляем сообщение в RabbitMQ
#     channel.basic_publish(
#         exchange='',
#         routing_key='new_video',
#         body=json.dumps(message)
#     )
#
#     connection.close()


# Функция для проверки файла в хранилище
def check_file_in_storage(file_name):
    try:
        return default_storage.exists(file_name)
    except Exception as e:
        logger.error(f"Ошибка при проверке существования файла {file_name} в хранилище: {e}")
        return False


def _is_video_file_changed(movie_instance):
    try:
        # Проверяем, если есть предыдущие сохраненные данные
        if movie_instance._state.adding or not movie_instance.pk:
            return False

        # Используем select_for_update чтобы получить зафиксированное состояние объекта
        old_instance = Movie.objects.select_for_update().get(pk=movie_instance.pk)
        # Проверяем, изменилось ли поле video_file
        return old_instance.video_file != movie_instance.video_file
    except Movie.DoesNotExist:
        logger.error(f"Фильм с id {movie_instance.pk} не найден")
        return False


def send_message_to_rabbitmq(film_id, file_name, file_url):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
        ))
        channel = connection.channel()

        # Объявляем очередь, если она еще не создана
        channel.queue_declare(queue='new_video', durable=True)

        message = {
            "film_id": str(film_id),
            "file_name": file_name,
            "url_original_video": file_url
        }

        # Отправляем сообщение в RabbitMQ
        channel.basic_publish(
            exchange='default_exchange',
            routing_key='new_video',
            body=json.dumps(message)
        )

        logger.info(f"Сообщение для фильма {film_id} отправлено в RabbitMQ.")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в RabbitMQ: {e}")
    finally:
        if connection:
            connection.close()


# Обработчик сигнала post_save
@receiver(post_save, sender=Movie)
def after_movie_save(sender, instance, created, **kwargs):
    # Получаем старую версию объекта до изменения

    if created or _is_video_file_changed(instance):
        # Получаем имя файла
        file_name = instance.video_file.name

        # Проверяем, загружен ли файл в MinIO (или другое дефолтное хранилище)
        # TODO добавить задачу селери для повторной проверки доступности файла
        if check_file_in_storage(file_name):
            logger.info(f"Файл {file_name} успешно загружен в хранилище.")
            try:
                send_message_to_rabbitmq(instance.id, file_name, instance.video_file.url)
            except Exception as e:
                logger.error(f"Ошибка при отправке сообщения в RabbitMQ для фильма {instance.id}: {e}")
        else:
            logger.warning(f"Файл {file_name} не найден в хранилище. Проверьте загрузку.")
