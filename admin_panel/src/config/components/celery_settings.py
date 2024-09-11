# CELERY
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

# CELERY_TASK_TRACK_STARTED = True  # запускает трекинг задач Celery

# Планировщик задач
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# CELERY_BROKER_TRANSPORT_OPTION = {'visibility_timeout': 3600}  # время ожидания видимости 1 час
CELERY_RESULT_BACKEND = 'django-db'  # указание для django_celery_results куда записывать результат выполнения задач
# CELERY_ACCEPT_CONTENT = ['application/json']  # это тип содержимого, разрешенный к получению
# CELERY_TASK_SERIALIZER = 'json'  # это строка, используемая для определения метода сериализации по умолчанию
# CELERY_RESULT_SERIALIZER = 'json'  # является типом формата сериализации результатов
#
# CELERY_TASK_DEFAULT_QUEUE = 'default'  # celery будет использовать это имя очереди
CELERY_IMPORTS = ("notification.tasks", )
