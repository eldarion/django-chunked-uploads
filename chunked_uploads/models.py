import datetime
import os

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db import models

from django.contrib.auth.models import User

from uuidfield import UUIDField


STORAGE_CLASS = getattr(settings, "CHUNKED_UPLOADS_STORAGE_CLASS", None)
if STORAGE_CLASS:
    storage = STORAGE_CLASS()
else:
    storage = None


def storage_path(obj, filename):
    if isinstance(obj, Upload):
        return os.path.join(obj.path_prefix(), filename).replace("/", "-")
        # @@@ this replacement is a hack to work around bug in django-storages cloud files backend
        # @@@ is this still necessary with cumulus?
    return os.path.join(obj.upload.path_prefix(), "chunk")


class Upload(models.Model):
    
    STATE_UPLOADING = 1
    STATE_COMPLETE = 2
    
    STATE_CHOICES = [
        (STATE_UPLOADING, "Uploading"),
        (STATE_COMPLETE, "Complete")
    ]
    
    user = models.ForeignKey(User, related_name="uploads")
    uuid = UUIDField(auto=True, unique=True)
    filename = models.CharField(max_length=250)
    filesize = models.IntegerField()
    upload = models.FileField(storage=storage, upload_to=storage_path)
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_UPLOADING)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return self.upload
    
    def path_prefix(self):
        s = str(self.uuid)
        return os.path.join(s[:2], s[2:4], s[4:6], s)
    
    def stitch_chunks(self):
        f = open(os.path.join(settings.MEDIA_ROOT, storage_path(self, self.filename)), "wb")
        for chunk in self.chunks.all().order_by("pk"):
            f.write(chunk.chunk.read())
        f.close()
        f = UploadedFile(open(f.name, "rb"))
        self.upload.save(self.filename, f)
        self.state = Upload.STATE_COMPLETE
        self.save()
        f.close()
    
    def uploaded_size(self):
        return self.chunks.all().aggregate(models.Sum("chunk_size")).get("chunk_size__sum")


class Chunk(models.Model):
    
    upload = models.ForeignKey(Upload, related_name="chunks")
    chunk = models.FileField(upload_to=storage_path)
    chunk_size = models.IntegerField()
    created_at = models.DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return self.chunk

