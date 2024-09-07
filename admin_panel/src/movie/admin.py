from django.contrib import admin
from django.contrib.admin import ModelAdmin

from movie.models import Movie


@admin.register(Movie)
class ImprovementTagAdmin(ModelAdmin):
    list_display = ('title', 'upload_date')
    search_fields = ('title', 'description')
