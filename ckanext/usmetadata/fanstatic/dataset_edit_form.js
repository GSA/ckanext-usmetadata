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

    if ($('form.dataset-form').size()) {

        datasetFormValid = true;

        $('#field-access-level-comment')
            .add('#field-license-new')
            .add('#field-temporal')
            .add('#field-data_dictionary')
            .add('#field-data_dictionary_type')
            .add('#field-conforms_to')
            .add('#field-homepage_url')
            .add('#field-language')
            .add('#field-primary-it-investment-uii')
            .add('#field-related_documents')
            .add('#field-release_date')
            .add('#field-system_of_records')
            .change(validate_dataset).change();

        $('form.dataset-form').submit(function (event) {
            if (!datasetFormValid) {
                event.preventDefault();
            }
        });
    }
});

function validate_dataset(){
    $.getJSON(
        '/api/2/util/resource/validate_dataset',
        {
            'rights': $('#field-access-level-comment').val(),
            'license_url': $('#field-license-new').val(),
            'temporal': $('#field-temporal').val(),
            'described_by': $('#field-data_dictionary').val(),
            'described_by_type': $('#field-data_dictionary_type').val(),
            'conforms_to': $('#field-conforms_to').val(),
            'landing_page': $('#field-homepage_url').val(),
            'language': $('#field-language').val(),
            'investment_uii': $('#field-primary-it-investment-uii').val(),
            'references': $('#field-related_documents').val(),
            'issued': $('#field-release_date').val(),
            'system_of_records': $('#field-system_of_records').val()
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
                datasetFormValid = false;
            } else {
                datasetFormValid = true;
            }
        }
    )
}
