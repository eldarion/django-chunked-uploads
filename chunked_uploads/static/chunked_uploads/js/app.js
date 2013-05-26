$(function(){    
    'use strict';
    $('.chunked_file_input').each(function(i, input) {
        var $input = $(input);
        progressWidget.insertAfter($input);
        var $upload_url = $input.data('upload_url');
        var $upload_done_url = $input.data('upload_done_url');
        var $upload_form_target = $('#' + $input.data('upload_target_id'));

        $input.fileupload({
            url: $upload_url,
            dataType: "json",
            replaceFileInput: false,
            start: function(e) {
              //$("#id_original_url").parents('.clearfix:first').hide(0);
              showProgress($(this).parent());
            },
            done: function (e, data) {
                var uuid = data.result[0].upload_uuid;
                $.ajax({
                        'dataType': "json",
                        'url': $upload_done_url.replace('abcdef0123456789', uuid),
                        'success': function(data, status, xhr) {
                            $upload_form_target.val(data.url);
                        }
                    });
            },
            progress: function (e, data) {
                var progress = parseInt(data.loaded / data.total * 100, 10);
                $(this).siblings(".progressbar").progressbar({value: progress});
            },
            send: function(e, data) {
                $(this).siblings(".fileinfo").html("<b>" + data.files[0].name + "</b> <i>" + data.files[0].size + "</i> bytes (" + data.files[0].type + ")");
                return true;
            },
            autoUpload: true,
            maxChunkSize: 1048576,
            multipart: false
        });
    });
});

