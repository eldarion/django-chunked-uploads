from django.forms.widgets import ClearableFileInput, HiddenInput
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text


class ChunkedFileInput(HiddenInput):
    class Media:
        js = (  'chunked_uploads/js/jquery.iframe-transport.js',
                'chunked_uploads/js/jquery.fileupload.js',
                'chunked_uploads/js/progress.js',
                'chunked_uploads/js/app.js')

    template = u'%(input)s %(hidden)s'
    template_with_initial = 'Currently: %(initial)s <br />Change: %(input)s %(hidden)s'

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        classes = attrs.get('class', '')
        classes += ' chunked_file_input'

        upload_url = reverse('uploads')
        complete_url = reverse('uploads_done', kwargs={'uuid': 'abcdef0123456789'})

        fakeattrs = {
                    'class': classes,
                    'data-upload_url': upload_url,
                    'data-upload_done_url': complete_url,
                    'type': 'file',
                    'data-upload_target_id': u'id_%s' % name,
            }

        fake = format_html('<input{0} />', flatatt(fakeattrs))

        ctx = {
            'initial': '',
            'hidden': super(ChunkedFileInput, self).render(name, value, attrs=attrs),
            'input': fake
        }
        template = self.template
        if value:
            template = self.template_with_initial
            ctx['initial'] = format_html('<a href="{1}">{1}</a>', value, force_text(value)) 

        return mark_safe(template % ctx)
