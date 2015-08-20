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

        $('#field-organizations')
            .add('#field-unique_id')
            .add('#field-access-level-comment')
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
            .change(validate_dataset);

        validate_dataset();

        $('form.dataset-form').submit(function (event) {
            if (!datasetFormValid) {
                event.preventDefault();
            }
        });


        $('#field-spatial').parents('div.control-group').addClass('exempt-allowed');
        $('#field-temporal').parents('div.control-group').addClass('exempt-allowed');
        $('#field-title').parents('div.control-group').addClass('exempt-allowed');
        $('#field-notes').parents('div.control-group').addClass('exempt-allowed');
        $('#field-modified').parents('div.control-group').addClass('exempt-allowed');
        $('#field-tags').parents('div.control-group').addClass('exempt-allowed');

        show_redacted_icons();
    }
});

function validate_dataset() {
    $.getJSON(
        '/api/2/util/resource/validate_dataset',
        {
            'pkg_name': $('[name="pkg_name"]').val(),
            'owner_org': $('#field-organizations').val(),
            'unique_id': $('#field-unique_id').val(),
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
    );
}

function show_redacted_icons() {
    var img = $('<img src="/redacted_icon.png" class="redacted-icon" alt="Mark as Redacted" title="Mark as Redacted">');
    $('.exempt-allowed .controls').before(img);

    $('.redacted-icon').click(redacted_icon_callback);
}

function redacted_icon_callback() {
    var controlsDiv = $(this).parent().children('.controls');
    if (controlsDiv.children('.exemption_reason').length){
        controlsDiv.children('.exemption_reason').toggle();
        return;
    }
    var id = controlsDiv.children(':first').attr('id').replace('field-','');
    var s = $('<select name="redacted_'+id+'" class="exemption_reason" />');
    $("<option />", {value: '', text: '== Select Exemption Reason =='}).appendTo(s);
    $("<option />", {value: 'B3',
        text: 'B3 - Specifically exempted from disclosure by statute provided …'}).appendTo(s);
    $("<option />", {value: 'B4',
        text: 'B4 - Trade secrets and commercial or financial information obtained from …'}).appendTo(s);
    $("<option />", {value: 'B5',
        text: 'B5 - Inter-agency or intra-agency memorandums or letters which …'}).appendTo(s);
    $("<option />", {value: 'B6',
        text: 'B6 - Personnel and medical files and similar files the disclosure of which …'}).appendTo(s);
    controlsDiv.append(s);
}