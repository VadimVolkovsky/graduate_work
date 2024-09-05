from fast_depends import Depends
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue, RabbitExchange

from core.config import settings
from cdn.src.minio_service import MinioService
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
    print(f'получено сообщение: {message}')
    worker.file_url = message.url_original_video  # берем из очереди ссылку на оригинальный файл в минио (presigned_url)
    worker.file_name = message.file_name  # берем из очереди название оригинального файла в минио
    worker.convert_video()
    await worker.upload_files_in_minio()
    # TODO добавить шаг update_db_info() - выполняет обновление записи в БД: добавляет ссылку на файлы m3u8 в Minio

# TODO подключить алхимию для работы с БД
# TODO вынести креды кролика из компоуза в .env
# TODO складывать фильмы в минио по папкам
# TODO сделать кастомную генерацию ссылки на m3u8 для сохранения в БД



### TODO для отладки отправки сообщений
async def _send_test_message():
    filename = 'SampleVideo_1280x720_10mb.mp4'
    minio_service = MinioService()
    print(f'DEBUG: загружаем файл в минио')
    minio_service.upload_file(filename)

    print(f'DEBUG: получаем presigned_url')
    url = minio_service.get_presigned_url(filename)
    message = MessageNewVideo(url_original_video=url, file_name=filename)
    print(f'DEBUG: публикуем месседж в очередь')
    await broker.publish(message, queue=queue_new_video, exchange=default_exchange)


### TODO для отладки отправки сообщений
if settings.debug:
    @app.after_startup
    async def test_publish():
        await _send_test_message()
