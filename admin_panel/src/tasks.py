from celery import shared_task


@shared_task(queue='new_video')
def task_send_message_to_rabbitmq(film_id, file_name, file_url):
    message = {
        "film_id": str(film_id),
        "file_name": file_name,
        "url_original_video": file_url
    }

    # Celery автоматически отправляет сообщения в RabbitMQ
    print(f"Отправляем сообщение в RabbitMQ: {message}")
    return message