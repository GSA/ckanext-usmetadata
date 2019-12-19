
  this.ckan.module('usmetadata-slug-preview-slug', function (jQuery) {
    return {
      options: {
        prefix: '',
        placeholder: '<slug>'
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
              'URL': this._('URL'),
              'Edit': this._('Edit')
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
        }
  
        // Watch for updates to the target field and update the hidden slug field
        // triggering the "change" event manually.
        sandbox.subscribe('slug-target-changed', function (value) {
          slug.val(value).trigger('change');
        });
      }
    };
  });
  