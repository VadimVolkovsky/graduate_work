from pydantic import BaseModel


class MessageNewVideo(BaseModel):
    """Схема сообщения в очереди"""
    url_original_video: str
    file_name: str
