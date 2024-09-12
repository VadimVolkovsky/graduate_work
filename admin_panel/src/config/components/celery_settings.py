import os

from kombu import Exchange, Queue

CELERY_BROKER_URL = 'amqp://guest:guest@rabbit:5672//'  # URL для RabbitMQ
CELERY_RESULT_BACKEND = 'django-db'  # Если используете django-celery-results
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# # Определите обменник
# default_exchange = Exchange('default', type='direct')
#
# # Определите очередь
# new_video_queue = Queue('new_video', exchange=default_exchange, routing_key='new_video')
#
# CELERY_QUEUES = (
#     new_video_queue,
# )
#
# CELERY_DEFAULT_EXCHANGE = 'default_exchange'
# CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
# CELERY_DEFAULT_ROUTING_KEY = 'new_video'

# CELERY_QUEUES = {
#     'default': {
#         'exchange': 'default',
#         'exchange_type': 'direct',
#         'binding_key': 'default',
#     },
#     'new_video': {
#         'exchange': 'default_exchange',
#         'exchange_type': 'direct',
#         'binding_key': 'new_video',
#     },
# }

RABBITMQ_HOST = os.environ.get('RABBIT_HOST', '127.0.0.1')
RABBITMQ_PORT = os.environ.get('RABBIT_PORT', '5672')
RABBITMQ_USER = os.environ.get('RABBIT_USER', '')
RABBITMQ_PASSWORD = os.environ.get('RABBIT_PASSWORD', '')
