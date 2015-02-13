$(document).ready(function () {
    //to be sure we are editing a resource
    if ($('form.dataset-resource-form').size()) {
        $('input[name="resource_type"]').change(
            function () {
                resource_type_change($(this).val());
            }
        );

        window.setInterval(function () {
            $('.resource-upload .btn').eq(2).remove();
            $('.resource-url .btn-remove-url').remove();
            resource_type_change($('input[name="resource_type"]:checked').val());
        }, 500);


        resourceFormValid = true;

        $('#field-image-url').after('<p></p>');
        $('#field-image-url').add('#field-format').change(verify_media_type);

        $('input[name="resource_type"]').change(verify_media_type);

        if (document.URL.indexOf('/new_resource/') > 10) {
            validate_resource();
        }

        $('input[name="resource_type"]').add('#field-format').add('#field-describedBy')
            .add('#field-describedByType').add('#field-conformsTo')
            .change(validate_resource);

        $('form.dataset-resource-form').submit(function (event) {
            // allow submitting empty resource on dataset create
            if (!$('input[name="url"]').val() && $('#field-resource-type-file').prop("checked")) {
                $('#field-resource-type-file').prop("checked", false);
            }
            if (!resourceFormValid) {
                event.preventDefault();
            }
        });
    }
});

function validate_resource() {
    $.getJSON(
        '/api/2/util/resource/validate_resource',
        {
            'url': $('#field-image-url').val(),
            'resource_type': $('input[name="resource_type"]:checked').val(),
            'format': $('#field-format').val(),
            'describedBy': $('#field-describedBy').val(),
            'describedByType': $('#field-describedByType').val(),
            'conformsTo': $('#field-conformsTo').val()
        },
        function (result) {
            $('input').next('p.bad').remove();
            $('input').next('p.warning').remove();
            $('input').parent().prev('label').removeClass('bad');

            if (typeof(result.ResultSet.Warnings) != "undefined") {
                var WarningObj = result.ResultSet.Warnings
                for (var key in WarningObj) {
                    if (WarningObj.hasOwnProperty(key)) {
                        $('#field-' + key).after('<p class="warning">Warning: ' + WarningObj[key] + '</p>');
                    }
                }
            }

            if (typeof(result.ResultSet.Invalid) != "undefined") {
                var InvalidObj = result.ResultSet.Invalid
                for (var key in InvalidObj) {
                    if (InvalidObj.hasOwnProperty(key)) {
                        $('#field-' + key).after('<p class="bad">' + InvalidObj[key] + '</p>');
                        $('#field-' + key).parent().prev('label').addClass('bad');
                    }
                }
                resourceFormValid = false;
            } else {
                resourceFormValid = true;
            }
        }
    )
}

function verify_media_type() {
    $('#field-image-url').next('p').replaceWith('<p></p>');

    var resource_type = $('input[name="resource_type"]:checked').val()
    var prepopulateMediaType = (resource_type == "file");
    if (resource_type == "upload") {
        return
    }

    $('#field-image-url').next('p').replaceWith('<p>Detecting Media Type...</p>');
    $.getJSON(
        '/api/2/util/resource/content_type',
        {'url': $('#field-image-url').val()},
        function (result) {
            if (typeof(result.ResultSet.CType) != "undefined") {
                var ct = result.ResultSet.CType;
                var status = result.ResultSet.Status;
                var reason = result.ResultSet.Reason;
                var sclass = (200 == status ? 'good' : 'bad')
                var currentMediaType = $('#field-format').val();

                var statusPrint = 'URL returned status <strong class="' + sclass + '">'
                    + status + ' (' + reason + ')</strong>';
                var ctypePrint = '<br />Media Type was detected as <strong>' + ct + '</strong>';
                var typeMatchPrint = '';

                if (200 != status) {
                    ctypePrint = '';
                } else if ('' == currentMediaType) {
                    if (prepopulateMediaType) {
                        $('#field-format').val(ct);
                        $('#s2id_field-format .select2-chosen').text(ct);
                        $('#s2id_field-format .select2-choice').removeClass('select2-default');
                        typeMatchPrint = '<br /><span class="good">Detected type matches ' +
                        'currently selected type <strong>' + ct + '</strong></span>';
                    }
                } else if (ct == currentMediaType) {
                    if (prepopulateMediaType) {
                        typeMatchPrint = '<br /><span class="good">Detected type matches ' +
                        'currently selected type <strong>' + ct + '</strong></span>';
                    }
                } else {
                    if (typeof(result.ResultSet.InvalidFormat) != "undefined") {
                        resourceFormValid = false;
                    }
                    if (prepopulateMediaType) {
                        typeMatchPrint = '<br /><span class="red">Detected type <strong>' + ct + '</strong> ' +
                        'does not match ' + 'currently selected type <strong>' + currentMediaType + '</strong></span>';
                    }
                }

                $('#field-image-url').next('p').replaceWith(
                    '<p>' + statusPrint + ctypePrint + typeMatchPrint + '</p>'
                );
            } else {
                var errorPrint = '';
                var errorClass = 'red';
                if ("undefined" != typeof(result.ResultSet.Error)) {
                    errorPrint = result.ResultSet.Error;
                } else if ("undefined" != typeof(result.ResultSet.ProtocolError)) {
                    errorPrint = result.ResultSet.ProtocolError;
                    errorClass = "weird";
                }
                $('#field-image-url').next('p').replaceWith(
                    '<p class="' + errorClass + '">Could not reach given url: ' + errorPrint + '</p>'
                );
            }
            validate_resource();
        })
}

function resource_type_change(val) {
    if (!val) return;
    $('.image-upload').show();
    switch (val) {
        case 'upload':
            $('.resource-upload').show();
            if ($('input[name="url"]').val()) {
                $('.resource-upload .btn').eq(1).show();
            }
            $('.resource-upload .btn').eq(0).show();
            $('#field-image-upload').show();
            $('.resource-url').hide();
            break;
        case 'api':
            if (!$('#field-format-readable').val()) {
                $('#field-format-readable').val('API');
            }
        default:
            $('.resource-upload').hide();
            $('.resource-upload .btn').first().hide();
            $('.resource-url').show();
    }
}