"use strict";

var RedactionControl = new function () {
    var obj = this;
    this.exempt_reasons = [
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

    this.render_redacted_input = function (key, val) {
        val = typeof val !== 'undefined' ? val : false;

        var currentInput = $(':input[name="' + key + '"]');
        var controlsDiv = currentInput.parents('.controls');
        if (!controlsDiv.length) {
            console.debug('controlsDiv not found for ' + key);
            return;
        }

        currentInput.css('background', '#ddd');

        var s = $('<select />', {
            name: "redacted_" + key,
            class: "exemption_reason",
            rel: key
        });


        $("<option />", {value: '', text: 'Select FOIA Exemption Reason for Redaction'}).appendTo(s);

        for (var index in this.exempt_reasons) {
            var reason = this.exempt_reasons[index];
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
    };

    this.show_redacted_input = function (key) {
        $('input[name="redacted_' + key + '"]').show();
    };

    this.redacted_icon_callback = function () {
        var controlsDiv = $(this).parent().children('.controls');
        if (controlsDiv.children('.exemption_reason').length) {
            if (!controlsDiv.children('.exemption_reason').val()) {
                controlsDiv.children('.exemption_reason').fadeToggle();
            }
            return;
        }
        var id = controlsDiv.children(':input').attr('name');
        obj.render_redacted_input(id);
        obj.show_redacted_input(id);
    };

    this.preload_redacted_inputs = function () {
        if ('undefined' != typeof redacted_json_raw) {  //  dataset resource (or distribution) way
            var redacted = redacted_json_raw;
        } else if($('#redacted_json').size()) {     // dataset way
            var redactedJson = $('#redacted_json');
            var redacted = $.parseJSON(redactedJson.val());
        }

        for (var field in redacted) {
            if (!redacted[field]) {
                continue;
            }
            obj.render_redacted_input(field.replace('redacted_', ''), redacted[field]);
            obj.show_redacted_input(field.replace('redacted_', ''));
        }
    };

    this.show_redacted_icons = function () {
        //var pencil = $('<i class="icon-eye-open redacted-icon" />', {
        //    alt: "Mark as Redacted",
        //    title: "Mark as Redacted"
        //})
        var img = $('<img src="/redacted_icon.png" class="redacted-icon" alt="Mark as Redacted" title="Mark as Redacted">');
        $('.exempt-allowed .controls').before(img);

        $('.redacted-icon').click(obj.redacted_icon_callback);
    };
}();