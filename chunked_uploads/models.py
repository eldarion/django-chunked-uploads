import datetime
import errno
import hashlib
import os

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.core.files.utils import FileProxyMixin
from django.db import models

from django.contrib.auth.models import User

from uuidfield import UUIDField


STORAGE_CLASS = getattr(settings, "CHUNKED_UPLOADS_STORAGE_CLASS", None)
if STORAGE_CLASS:
    storage = STORAGE_CLASS()
else:
    storage = None


STORAGE_PATH = getattr(settings, "CHUNKED_UPLOADS_STORAGE_PATH", None)
if STORAGE_PATH:
    storage_path = STORAGE_PATH
else:
    storage_path = lambda obj, fname: os.path.join("chunked_uploads", obj.uuid, fname)


CHUNKS_STORAGE_PATH = getattr(settings, "CHUNKED_UPLOADS_CHUNKS_STORAGE_PATH", None)
if CHUNKS_STORAGE_PATH:
    chunks_storage_path = CHUNKS_STORAGE_PATH
else:
    chunks_storage_path = lambda obj, fname: os.path.join("chunked_uploads", obj.upload.uuid, "chunks", "chunk")



class File(FileProxyMixin):
    """
    This is needed as there was a bug pre-1.4 django with getting
    size off of a file object
    """
    def __init__(self, file):
        self.file = file
    
    @property
    def size(self):
        pos = self.file.tell()
        self.file.seek(0, os.SEEK_END)
        size = self.file.tell()
        self.file.seek(pos)
        return size


class Upload(models.Model):
    
    STATE_UPLOADING = 1
    STATE_COMPLETE = 2
    STATE_STITCHED = 3
    STATE_UPLOAD_ERROR = 4
    
    STATE_CHOICES = [
        (STATE_UPLOADING, "Uploading"),
        (STATE_COMPLETE, "Complete - Chunks Uploaded"),
        (STATE_STITCHED, "Complete - Stitched"),
        (STATE_UPLOAD_ERROR, "Upload Error")
    ]
    
    user = models.ForeignKey(User, related_name="uploads")
    uuid = UUIDField(auto=True, unique=True)
    filename = models.CharField(max_length=250)
    filesize = models.IntegerField()
    upload = models.FileField(max_length=250, storage=storage, upload_to=storage_path)
    md5 = models.CharField(max_length=32, blank=True)
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_UPLOADING)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return u"<%s - %s bytes - pk: %s, uuid: %s, md5: %s>" % (
            self.filename, self.filesize, self.pk, self.uuid, self.md5
        )
    
    def stitch_chunks(self):
        fname = os.path.join(
            self.upload.storage.location,
            storage_path(self, self.filename + ".tmp")
        )
        try:
            os.makedirs(os.path.dirname(fname))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        fp = open(fname, "wb")
        m = hashlib.md5()
        for chunk in self.chunks.all().order_by("pk"):
            bytes = chunk.chunk.read()
            m.update(bytes)
            fp.write(bytes)
        fp.close()
        f = File(open(fname, "rb"))
        self.upload.save(
            name=fname.replace(".tmp", ""),
            content=UploadedFile(
                file=f,
                name=fname.replace(".tmp", ""),
                size=f.size
            )
        )
        self.md5 = m.hexdigest()
        self.state = Upload.STATE_STITCHED
        self.save()
        os.remove(fname)
    
    def uploaded_size(self):
        return self.chunks.all().aggregate(
            models.Sum("chunk_size")
        ).get("chunk_size__sum")


class Chunk(models.Model):
    
    upload = models.ForeignKey(Upload, related_name="chunks")
    chunk = models.FileField(upload_to=chunks_storage_path)
    chunk_size = models.IntegerField()
    created_at = models.DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return u"<Chunk pk=%s, size=%s, upload=(%s, %s)>" % (
            self.pk, self.chunk_size, self.upload.pk, self.upload.uuid
        )

