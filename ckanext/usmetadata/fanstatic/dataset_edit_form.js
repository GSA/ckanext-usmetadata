/**
 * Created by ykhadilkar
 */
$(document).ready(function () {
    $("#field-is_parent").change(function () {
        $val = $("#field-is_parent").val();

        if ($val == 'true') {
            $(".control-group-dataset-parent").hide();
            $("#field-parent_dataset").val("");
        } else {
            $(".control-group-dataset-parent").show();
            //remove current dataset from parent dataset list
            //$("#field-parent_dataset option[value='"+$('[name="pkg_name"]').val()+"']").remove();
            //$("#field-parent_dataset").prepend("<option value='' selected='selected'></option>");

        }
    }).change();

    //if ($('form.dataset-form').size()) {
    //    $('input[name="resource_type"]').add('#field-format').add('#field-describedBy')
    //        .add('#field-describedByType').add('#field-conformsTo')
    //        .change(validate_resource).change();
    //}
});

function validate_dataset(){
    $.getJSON(
        '/api/2/util/resource/validate_dataset',
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
