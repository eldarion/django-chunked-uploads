# django-chunked-uploads

This is an app for your Django project to enable large uploads using the Blob API to chunk the files client side and send chunks that are re-assembled server side.


## Changelist

### 0.4
  * adds proper requirements
  * large refactor to provide a model field that mimics FileField but relies, by default, on a widgetized chunked uploader
