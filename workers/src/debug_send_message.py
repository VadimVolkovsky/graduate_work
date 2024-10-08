import asyncio

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue, RabbitExchange

from common_settings.config import settings
from schemas.message_schema import MessageNewVideo

### TODO данный файл используется для отладки отправки сообщений в очередь

broker = RabbitBroker(
    f"amqp://{settings.rabbit_user}:{settings.rabbit_password}@{settings.rabbit_host}:{settings.rabbit_port}/")

app = FastStream(broker)
queue_new_video = RabbitQueue("new_video")
default_exchange = RabbitExchange("default_exchange")


async def send_message():
    print('отправляем сообщение в RabbitMQ')
    # необходимо предварительно загрузить тестовое видео в Minio и вставить ниже presigned_url на него.
    # заменить в ссылке хост на MINIO_HOST из .env
    url_original_video = f'http://localhost:9000/graduate-work-bucket/SampleVideo_1280x720_10mb.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=minio_user%2F20240903%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20240903T075851Z&X-Amz-Expires=43200&X-Amz-SignedHeaders=host&X-Amz-Signature=0384077017174306da6de235d6510c7e5f124e2f3c45dbe37242086011ceea96'
    file_name = 'SampleVideo_1280x720_10mb.mp4'  # тестовое видео хранится в /media
    message = MessageNewVideo(url_original_video=url_original_video, file_name=file_name)
    await broker.publish(message, queue=queue_new_video, exchange=default_exchange)


async def main():
    await broker.connect()
    await send_message()
    await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
