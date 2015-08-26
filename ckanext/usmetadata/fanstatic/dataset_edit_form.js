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
        preload_redacted_inputs();
        //$('.exemption_reason').renderEyes();
        redacted_bootstrap();
        $(':input[name="public_access_level"]').change(redacted_bootstrap);
    }
});

//$.fn.extend({
//    renderEyes: function () {
//        if ($(this).val()) {
//            $(this).parents('.control-group').children('.redacted-icon').removeClass('icon-eye-open');
//            $(this).parents('.control-group').children('.redacted-icon').addClass('icon-eye-close');
//        } else {
//            $(this).parents('.control-group').children('.redacted-icon').removeClass('icon-eye-close');
//            $(this).parents('.control-group').children('.redacted-icon').addClass('icon-eye-open');
//        }
//    }
//});

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

function preload_redacted_inputs() {
    if (!$('#redacted_json').length) {
        return;
    }
    var redacted = $.parseJSON($('#redacted_json').val());
    for (var field in redacted) {
        render_redacted_input(field.replace('redacted_', ''), redacted[field]);
        show_redacted_input(field.replace('redacted_', ''));
    }
}

function show_redacted_icons() {
    //var pencil = $('<i class="icon-eye-open redacted-icon" />', {
    //    alt: "Mark as Redacted",
    //    title: "Mark as Redacted"
    //})
    var img = $('<img src="/redacted_icon.png" class="redacted-icon" alt="Mark as Redacted" title="Mark as Redacted">');
    $('.exempt-allowed .controls').before(img);

    $('.redacted-icon').click(redacted_icon_callback);
}

var exempt_reasons = [
    {
        'value': 'B3',
        'short': 'B3 - Specifically exempted from disclosure by statute provided …',
        'full': "Specifically exempted from disclosure by statute (other than FOIA), provided that such " +
        "statute (A) requires that the matters be withheld from the public in such a manner as to leave no" +
        " discretion on the issue, or (B) establishes particular criteria for withholding or refers to" +
        " particular types of matters to be withheld."
    },
    {
        'value': 'B4',
        'short': 'B4 - Trade secrets and commercial or financial information obtained from …',
        'full': "Trade secrets and commercial or financial information obtained from a person" +
        " and privileged or confidential."
    },
    {
        'value': 'B5',
        'short': 'B5 - Inter-agency or intra-agency memorandums or letters which …',
        'full': "Inter-agency or intra-agency memorandums or letters which would not be available by law " +
        "to a party other than an agency in litigation with the agency."
    },
    {
        'value': 'B6',
        'short': 'B6 - Personnel and medical files and similar files the disclosure of which …',
        'full': "Personnel and medical files and similar files the disclosure of which would constitute" +
        " a clearly unwarranted invasion of personal privacy."
    }
];

function render_redacted_input(key, val) {
    val = typeof val !== 'undefined' ? val : false;

    var controlsDiv = $(':input[name="' + key + '"]').parents('.controls');
    if (!controlsDiv.length) {
        console.debug('controlsDiv not found for ' + key);
        return;
    }

    $(':input[name="' + key + '"]').css('background', '#ddd');

    var s = $('<select />', {
        name: "redacted_" + key,
        class: "exemption_reason",
        rel: key
    });


    $("<option />", {value: '', text: 'Select FOIA Exemption Reason for Redaction'}).appendTo(s);

    for (var index in exempt_reasons) {
        reason = exempt_reasons[index];
        var options = {
            value: reason.value, alt: reason.full, title: reason.full,
            text: reason.short
        };
        if (reason.value == val) {
            options['selected'] = 'selected';
        }
        $("<option />", options).appendTo(s);
    }
    //s.change(function(){$(this).renderEyes();});
    controlsDiv.append(s);
}

function show_redacted_input(key) {
    $('input[name="redacted_' + key + '"]').show();
}

function redacted_icon_callback() {
    var controlsDiv = $(this).parent().children('.controls');
    if (controlsDiv.children('.exemption_reason').length) {
        if (!controlsDiv.children('.exemption_reason').val()) {
            controlsDiv.children('.exemption_reason').fadeToggle();
        }
        return;
    }
    var id = controlsDiv.children(':input').attr('name');
    render_redacted_input(id);
    show_redacted_input(id);
}

function redacted_bootstrap() {
    var level = $(':input[name="public_access_level"]').val();
    if ('public' == level) {
        $('.redacted-icon').add('.exemption_reason').hide();
        return;
    }
    $('.redacted-icon').show();
    $('.exemption_reason').filter(function() { return $(this).val() !== ""; }).show();
}