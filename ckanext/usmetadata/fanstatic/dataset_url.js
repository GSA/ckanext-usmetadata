this.ckan.module('usmetadata-slug-preview-slug', function (jQuery, _) {
    return {
        options: {
            prefix: '',
            placeholder: '<slug>',
            i18n: {
                url: _('URL'),
                edit: _('Edit')
            }
        },

        initialize: function () {
            var sandbox = this.sandbox;
            var options = this.options;
            var el = this.el;
            var _ = sandbox.translate;

            var slug = el.slug();
            var parent = slug.parents('.control-group');
            var preview;

            if (!(parent.length)) {
                return;
            }

            // Leave the slug field visible
            if (!parent.hasClass('error')) {
                preview = parent.slugPreview({
                    prefix: options.prefix,
                    placeholder: options.placeholder,
                    i18n: {
                        'URL': this.i18n('url'),
                        'Edit': this.i18n('edit')
                    }
                });

                // If the user manually enters text into the input we cancel the slug
                // listeners so that we don't clobber the slug when the title next changes.
                slug.keypress(function () {
                    if (event.charCode) {
                        sandbox.publish('slug-preview-modified', preview[0]);
                    }
                });

                sandbox.publish('slug-preview-created', preview[0]);

                // Horrible hack to make sure that IE7 rerenders the subsequent
                // DOM children correctly now that we've render the slug preview element
                // We should drop this horrible hack ASAP
                if (jQuery('html').hasClass('ie7')) {
                    jQuery('.btn').on('click', preview, function () {
                        jQuery('.controls').ie7redraw();
                    });
                    preview.hide();
                    setTimeout(function () {
                        preview.show();
                        jQuery('.controls').ie7redraw();
                    }, 10);
                }
            }

            // Watch for updates to the target field and update the hidden slug field
            // triggering the "change" event manually.
            sandbox.subscribe('slug-target-changed', function (value) {
                slug.val(value).trigger('change');
            });
            //Hiding preview - Issue # 71
            if (jQuery("#dataset_status_id").val() !== 'draft') {
                preview.hide();
            }
        }
    };
});

//Bug fix Github # 166
//Inventory_user is navigated to the Error 404 page_when last breadcrumb is selected on the resource uplaod page in IE.
window.onload = function () {
    jQuery("#content .toolbar .breadcrumb .active a").prop("href", document.URL)
};