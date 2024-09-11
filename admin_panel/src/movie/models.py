import uuid

from django.db import models

from movie.utils import upload_to_uuid


class Movie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_file = models.FileField(upload_to=upload_to_uuid)
    hls_playlist_url = models.URLField(null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pk} | {self.title}'
