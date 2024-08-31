import asyncio

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue, RabbitExchange

from core.config import settings
from schemas.message_schema import MessageNewVideo

### TODO данный файл используется для отладки отправки сообщений в очередь

broker = RabbitBroker(
    f"amqp://{settings.rabbit_user}:{settings.rabbit_password}@{settings.rabbit_host}:{settings.rabbit_port}/")

app = FastStream(broker)
queue_new_video = RabbitQueue("new_video")
default_exchange = RabbitExchange("default_exchange")


async def send_message():
    print('отправляем сообщение в RabbitMQ')
    # необходимо предварительно загрузить тестовое видео в Minio и вставить ниже presigned_url на него
    url_original_video = 'https://play.min.io/volkovskiy-test-bucket-33/SampleVideo_1280x720_10mb.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=Q3AM3UQ867SPQQA43P2F%2F20240831%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20240831T090728Z&X-Amz-Expires=43200&X-Amz-SignedHeaders=host&X-Amz-Signature=b6c2cf78e28f50877fa5d95f5e7101f30eb0e6b0a7874a752b110bd2de8da606'
    file_name = 'SampleVideo_1280x720_10mb.mp4'  # тестовое видео хранится в /media
    message = MessageNewVideo(url_original_video=url_original_video, file_name=file_name)
    await broker.publish(message, queue=queue_new_video, exchange=default_exchange)


async def main():
    await broker.connect()
    await send_message()
    await asyncio.sleep(1)


if "__main__" == __name__:
    asyncio.run(main())
