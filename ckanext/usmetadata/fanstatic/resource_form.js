$(document).ready(function(){
    $('input[name="resource_type"]').change(
        function(){resource_type_change($(this).val());}
    );

    $('form.dataset-resource-form').submit(function(){
        if (!$('input[name="url"]').val()) {
            $('input[name="resource_type"]').prop("checked", false);
        }
    })

    window.setInterval(function(){
        $('.resource-upload .btn').eq(2).remove();
        $('.resource-url .btn-remove-url').remove();
        resource_type_change($('input[name="resource_type"]:checked').val());
    }, 500);

    $('#field-image-url').after('<p></p>');

    $('#field-image-url').change(function () {
        $('#field-image-url').next('p').replaceWith('<p>Detecting Media Type...</p>');
        $.getJSON(
            '/api/2/util/resource/content_type',
            {'url': $('#field-image-url').val()},
            function (result) {
                if (typeof(result.ResultSet.Result) != "undefined") {
                    var ct = result.ResultSet.Result;
                    $('#field-format').val(ct);
                    $('#s2id_field-format .select2-chosen').text(ct);
                    $('#s2id_field-format .select2-choice').removeClass('select2-default');
                    $('#field-image-url').next('p').replaceWith('<p>Media Type was detected as <strong>' + ct + '</strong></p>');
                } else {
                    $('#field-image-url').next('p').replaceWith('<p>Media Type was not detected</p>');
                }
            })
    })
});

function resource_type_change(val)
{
    if (!val) return;
    $('.image-upload').show();
    switch(val) {
        case 'upload':
            $('.resource-upload').show();
            if ($('input[name="url"]').val()) {
                $('.resource-upload .btn').eq(1).show();
            }
            $('.resource-upload .btn').eq(0).show();
            $('#field-image-upload').show();
            $('.resource-url').hide();
            break;
        default:
            $('.resource-upload').hide();
            $('.resource-upload .btn').first().hide();
            $('.resource-url').show();
    }
}