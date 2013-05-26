from django.forms import FilePathField, FileField

from chunked_uploads.widgets import ChunkedFileInput


class ChunkedFileField(FilePathField):
    widget = ChunkedFileInput

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = ChunkedFileInput
        super(ChunkedFileField, self).__init__(*args, **kwargs)

    def valid_value(self, val):
        return True

