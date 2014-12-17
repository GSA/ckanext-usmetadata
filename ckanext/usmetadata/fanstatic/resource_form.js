$(document).ready(function(){
    $('input[name="resource_type"]').change(
        function(){resource_type_change($(this).val());}
    );
});

function resource_type_change(val)
{
    switch(val) {
        case 'upload':
            $('.resource-upload').add('#field-image-upload').show();
            $('.resource-upload .btn').first().show();
            $('.resource-url').hide();
            break;
        default:
            $('.resource-upload').add('#field-image-upload').hide();
            $('.resource-upload .btn').first().hide();
            $('.resource-url').show();
    }

}