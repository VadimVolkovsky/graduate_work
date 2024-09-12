from fast_depends import Depends
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue, RabbitExchange

from cdn.src.minio_service import MinioService
from common_settings.logger import logger
from common_settings.config import settings
from schemas.message_schema import MessageNewVideo
from worker_video_preparation import get_worker

broker = RabbitBroker(
    f"amqp://{settings.rabbit_user}:{settings.rabbit_password}@{settings.rabbit_host}:{settings.rabbit_port}/")

app = FastStream(broker)
queue_new_video = RabbitQueue("new_video")
default_exchange = RabbitExchange("default_exchange")


@broker.subscriber(queue_new_video, default_exchange)
async def handle_message_from_queue(message: MessageNewVideo, worker=Depends(get_worker)):
    """
    Обработчик сообщений из очереди.
    После получения нового соообщения, запускается конвертация видеофайла в формат m3u8,
    далее происходит загрузка сконвертированных файлов в хранилище Minio.

    Синтаксис команды для локального запуска обработчика:
    faststream run main:app
    """
    logger.info(f'получено сообщение: {message}')
    worker.film_id = message.film_id
    worker.file_url = message.url_original_video  # берем из очереди ссылку на оригинальный файл в минио (presigned_url)
    worker.file_name = message.file_name  # берем из очереди название оригинального файла в минио
    worker.convert_video()
    await worker.upload_files_in_minio()
    # TODO добавить шаг update_db_info() - выполняет обновление записи в БД: добавляет ссылку на файлы m3u8 в Minio


### TODO для отладки отправки сообщений
async def _send_test_message():
    film_id = 'cc733c92-6853-45f6-8e49-bec741188ebb'
    filename = 'SampleVideo_1280x720_10mb.mp4'
    minio_service = MinioService()
    logger.info(f'DEBUG: загружаем файл {filename} в минио')
    remote_filepath = minio_service.upload_file(film_id, filename)
    logger.info(f'DEBUG: получаем presigned_url')
    url = minio_service.get_presigned_url(remote_filepath)
    message = MessageNewVideo(film_id=film_id, url_original_video=url, file_name=filename)
    logger.info(f'DEBUG: публикуем месседж в очередь')
    await broker.publish(message, queue=queue_new_video, exchange=default_exchange)


### TODO для отладки отправки сообщений - нужно включить в settings debug=True
if settings.debug_queue_message:
    @app.after_startup
    async def test_publish():
        await _send_test_message()
