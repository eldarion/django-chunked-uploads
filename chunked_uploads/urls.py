from django.conf.urls.defaults import *

from chunked_uploads.views import UploadView


urlpatterns = patterns("",
    url(r"^upload/$", UploadView.as_view(), name="uploads"),
    url(r"^(?P<pk>\d+)/delete/$", UploadView.as_view(), name="uploads_delete"),
)
