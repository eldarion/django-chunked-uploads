import json

from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View

from django.contrib.auth.decorators import login_required

from chunked_uploads.models import Upload, Chunk


class LoginRequiredView(View):
    
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredView, self).dispatch(request, *args, **kwargs)


@csrf_exempt
def complete_upload(request, uuid):
    up = get_object_or_404(Upload, uuid=uuid)
    if up.filesize == up.uploaded_size():
        up.state = Upload.STATE_COMPLETE
    else:
        up.state = Upload.STATE_UPLOAD_ERROR
    up.save()
    if "upload-uuid" in request.session:
        del request.session["upload-uuid"]
    return HttpResponse()


class UploadView(LoginRequiredView):
    
    def _add_status_response(self, upload):
        return {
            "name": upload.filename,
            "type": "",
            "size": upload.uploaded_size(),
            "progress": "",
            "thumbnail_url": "",
            "url": upload.chunks.all()[0].chunk.url,  # @@@ this is wrong
            "delete_url": reverse("uploads_delete", kwargs={"pk": upload.pk}),
            "delete_type": "DELETE",
            "upload_uuid": str(upload.uuid)
        }
    
    def handle_chunk(self):
        f = ContentFile(self.request.raw_post_data)
        
        if "upload-uuid" in self.request.session:
            try:
                u = Upload.objects.get(uuid=self.request.session["upload-uuid"])
                if u.state in [Upload.STATE_COMPLETE, Upload.STATE_UPLOAD_ERROR]:
                    del self.request.session["upload-uuid"]
            except Upload.DoesNotExist:
                del self.request.session["upload-uuid"]
        
        if "upload-uuid" not in self.request.session:
            u = Upload.objects.create(
                user=self.request.user,
                filename=self.request.META["HTTP_X_FILE_NAME"],
                filesize=self.request.META["HTTP_X_FILE_SIZE"]
            )
            self.request.session["upload-uuid"] = str(u.uuid)
        
        c = Chunk(upload=u)
        c.chunk.save(u.filename, f, save=False)
        c.chunk_size = c.chunk.size
        c.save()
        
        data = []
        data.append(self._add_status_response(u))
        
        return HttpResponse(json.dumps(data), mimetype="application/json")
    
    def handle_whole(self):
        f = self.request.FILES.get("file")
        u = Upload.objects.create(
            user=self.request.user,
            filename=f.name,
            filesize=f.size
        )
        Chunk.objects.create(
            upload=u,
            chunk=f
        )
        u.state = Upload.STATE_COMPLETE
        u.save()
        u.stitch_chunks()
        data = []
        data.append(self._add_status_response(u))
        return HttpResponse(json.dumps(data), mimetype="application/json")
    
    def get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps([{}]))
    
    def post(self, request, *args, **kwargs):
        if request.META.get("HTTP_X_FILE_NAME"):
            return self.handle_chunk()
        else:
            return self.handle_whole()
    
    def delete(self, request, *args, **kwargs):
        upload = get_object_or_404(Upload, pk=kwargs.get("pk"))
        upload.delete()  # Make sure this cascade deletes it's chunks
        return HttpResponse(json.dumps({}), mimetype="application/json")
