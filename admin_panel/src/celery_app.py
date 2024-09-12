from __future__ import absolute_import, unicode_literals
import os

from celery import Celery

# Установите переменную окружения для Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('admin_panel')

# Загрузите конфигурацию Celery из Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически откройте задачи из всех зарегистрированных приложений Django
app.autodiscover_tasks()
