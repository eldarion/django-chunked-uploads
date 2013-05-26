import os

from django.db import models
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models.fields.files import FieldFile, FileDescriptor

from chunked_uploads import forms
from chunked_uploads.models import storage_path, storage


class ChunkedFileField(models.FilePathField):
    attr_class = FieldFile
    descriptor_class = FileDescriptor
    storage = storage if storage else default_storage

    def __init__(self, *args, **kwargs):
        kwargs['path'] = os.path.join(settings.MEDIA_ROOT, 'chunked_uploads') ## TODO: this should be getting the path from the storage

        return super(ChunkedFileField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.ChunkedFileField}
        defaults.update(kwargs)
        ff =  super(ChunkedFileField, self).formfield(**defaults)
        return ff

    def contribute_to_class(self, cls, name):
        super(ChunkedFileField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, self.descriptor_class(self))
