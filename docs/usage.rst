.. _usage:

Usage
=====

::
    <script type="text/javascript" src="{{ STATIC_URL }}chunked_uploads/js/jquery.iframe-transport.js"></script>
    <script type="text/javascript" src="{{ STATIC_URL }}chunked_uploads/js/jquery.fileupload.js"></script>
    <script type="text/javascript" src="{{ STATIC_URL }}chunked_uploads/js/progress.js"></script>
    <script type="text/javascript">
        $(function() {
            $("#fileupload").append(progressWidget);
            
            if (typeof(self.WebKitBlobBuilder) == "undefined" && typeof(BlobBuilder) == "undefined") {
                var message = $("<p />").addClass("info").text("Currently upload functionality is only supported by Chrome.");
                $("#fileupload").html(message);
            } else {
                'use strict';
                
                $("#fileupload").fileupload({
                    url: "{% url uploads %}",
                    dataType: "json",
                    start: function(e) {
                      $("#id_original_url").parents('.clearfix:first').hide(0);
                      showProgress($(this));
                    },
                    done: function (e, data) {
                        $("#id_upload_uuid").val(data.result[0].upload_uuid);
                        $("input[name=Submit]").attr("disabled", false);
                    },
                    progress: function (e, data) {
                        var progress = parseInt(data.loaded / data.total * 100, 10);
                        $(this).find(".progressbar").progressbar({value: progress});
                    },
                    send: function(e, data) {
                        $(this).find("input[type=file]").hide();
                        $(this).find(".fileinfo").html("<b>" + data.files[0].name + "</b> <i>" + data.files[0].size + "</i> bytes (" + data.files[0].type + ")");
                        return true;
                    },
                    autoUpload: true,
                    maxChunkSize: 1048576,
                    multipart: false
                });
            }
        });
    </script>