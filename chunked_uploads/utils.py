from chunked_uploads.models import Upload, Chunk


def handle_upload(uploaded_file, who):
    """
    Expects to handle an individual file from request.FILES[name]
    
    Returns an Upload object
    """
    u = Upload.objects.create(
        user=who,
        filename=uploaded_file.name,
        filesize=uploaded_file.size
    )
    Chunk.objects.create(
        upload=u,
        chunk=uploaded_file,
        chunk_size=uploaded_file.size
    )
    u.state = Upload.STATE_COMPLETE
    u.save()
    u.stitch_chunks()
    return u