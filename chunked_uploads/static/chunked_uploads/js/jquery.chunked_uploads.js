jQuery(function($) {

    var ChunkedUpload = function(form, options) {
        this.options = $.extend({}, $.fn.phileo.defaults, options);
        this.$form = $(form);

        this.$count = $(this.options.count);

        var self = this;
        this.$form.submit(function(event) {
            event.preventDefault();

            $.ajax({
                url: self.$form.attr('action'),
                type: "POST",
                data: self.$form.serialize(),
                statusCode: {
                    200: function(data, textStatus, jqXHR) {
                        self.$count.text(data.likes_count);
                        self.$form[data.liked ? 'addClass' : 'removeClass'](self.options.toggle_class);
                    }
                }
            });
        });
    };

    $.fn.phileo = function(options) {
        $(this).each(function(i, el) {
            var chunked_upload = new ChunkedUpload(el, options);
            $(el).data('DjangoChunkedUpload', {instance: chunked_upload});
        });
        return this;
    };

    $.fn.phileo.defaults = {
        toggle_class: 'phileo-liked',
        count: false
    };
});
