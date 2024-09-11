import os
from typing import Any

from django.utils.text import slugify


def upload_to_uuid(instance: Any, filename: str) -> str:
    model_name = instance.__class__.__name__.lower()
    ext = filename.split('.')[-1]
    new_filename = f'{instance.id}.{ext}'
    return os.path.join(model_name, new_filename)
