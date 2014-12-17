$(document).ready(function(){
    $('input[name="resource_type"]').change(
        function(){resource_type_change($(this).val());}
    );
});

window.setInterval(function(){
  /// call your function here
    $('.resource-upload .btn').eq(2).remove();
    $('.resource-url .btn-remove-url').remove();
    resource_type_change($('input[name="resource_type"]:checked').val());
}, 500);

function resource_type_change(val)
{
    switch(val) {
        case 'upload':
            $('.resource-upload').show();
            if ($('input[name="url"]').val()) {
                $('.resource-upload .btn').eq(1).show();
            } else {
                $('.resource-upload .btn').eq(0).show();
            }
            $('#field-image-upload').show();
            $('.resource-url').hide();
            break;
        default:
            $('.resource-upload').hide();
            $('.resource-upload .btn').first().hide();
            $('.resource-url').show();
    }
}