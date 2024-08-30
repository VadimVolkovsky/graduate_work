from fast_depends import Depends
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue, RabbitExchange

from worker_video_preparation import MessageNewVideo, get_worker
# from workers.src.worker_video_preparation import get_worker, MessageNewVideo

broker = RabbitBroker(
    # f"amqp://{settings.rabbit_user}:{settings.rabbit_password}@{settings.rabbit_host}:{settings.rabbit_port}/")
    f"amqp://guest:guest@localhost:5672/")
### TODO пофиксить запуск в контейнерах (воркер не видит контейнер кролика)

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
