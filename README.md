# django-chunked-uploads

This is an app for your Django project to enable large uploads using the Blob API to chunk the files client side and send chunks that are re-assembled server side.

## Installation

* To install

    python setup.py install

* Add ``'chunked_uploads'`` to your ``INSTALLED_APPS`` setting

    INSTALLED_APPS = (
        # other apps
        "chunked_uploads",
    )

## Usage

* Ensure the template your load the form in has jQuery / jQuery.ui

    <script src="//ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js"></script>
    <script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js"></script>

* Set up your model...
    from chunked_uploads.fields import ChunkedFileField

    class MyModel(...):
        file_field = ChunkedFileField()

* Register uploader urls...

    urlpatterns = patterns('',
        url(r'uploader/', include('chunked_uploads.urls')),
        ...
    )


## Todo
* Currently upload\_to/path is not customizable
* allow for custom class to be used for Uploads 


## Changelist

### 0.4
* adds proper requirements
* large refactor to provide a model field that mimics FileField but relies, by default, on a widgetized chunked uploader

### 0.2
* removed hard dependency on cumulus storage backend

### 0.1
* initial release

