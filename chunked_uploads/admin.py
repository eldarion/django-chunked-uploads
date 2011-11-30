from django.contrib import admin

from chunked_uploads.models import Upload, Chunk


admin.site.register(Upload)
admin.site.register(Chunk)