$(document).ready(function(){
    $('input[name="resource_type"]').change(
        function(){resource_type_change($(this).val());}
    );
});

window.setInterval(function(){
  /// call your function here
    $('.resource-upload .btn').eq(2).remove();
    $('.resource-url .btn-remove-url').remove();
}, 500);

function resource_type_change(val)
{
    switch(val) {
        case 'upload':
            $('.resource-upload').show();
            $('#field-image-upload').show();
            $('.resource-upload .btn').first().show();
            $('.resource-url').hide();
            break;
        default:
            $('.resource-upload').hide();
            $('.resource-upload .btn').first().hide();
            $('.resource-url').show();
    }
}