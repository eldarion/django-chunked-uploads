from django.conf.urls.defaults import *

from chunked_uploads.views import UploadView, complete_upload


urlpatterns = patterns("",
    url(r"^upload/done/(?P<uuid>[0-9a-f]+)/$", complete_upload, name="uploads_done"),
    url(r"^upload/$", UploadView.as_view(), name="uploads"),
    url(r"^(?P<pk>\d+)/delete/$", UploadView.as_view(), name="uploads_delete"),
)
