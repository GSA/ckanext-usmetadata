import logging

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

# FIXME OrderedDict should be available via the toolkit
try:
    from collections import OrderedDict # 2.7
except ImportError:
    from sqlalchemy.util import OrderedDict

def create_access_levels():
    '''Create accessLevels vocab and tags, if they don't exist already.'''
    user = tk.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}
    try:
        data = {'id': 'accessLevels'}
        tk.get_action('vocabulary_show')(context, data)
        logging.info("Example genre vocabulary already exists, skipping.")
    except tk.ObjectNotFound:
        logging.info("Creating vocab 'accessLevels'")
        data = {'name': 'accessLevels'}
        vocab = tk.get_action('vocabulary_create')(context, data)
        for tag in (u'public', u'restricted', u'private'):
            logging.info(
                    "Adding tag {0} to vocab 'accessLevels'".format(tag))
            data = {'name': tag, 'vocabulary_id': vocab['id']}
            tk.get_action('tag_create')(context, data)


def accessLevels():
    '''Return the list of access levels from the accessLevels vocabulary.'''
    create_access_levels()
    try:
        access_levels = tk.get_action('tag_list')(
                data_dict={'vocabulary_id': 'accessLevels'})
        return accessLevels
    except tk.ObjectNotFound:
        return None

class IFacetPlugin(plugins.SingletonPlugin):

    plugins.implements(plugins.IFacets, inherit=True)

    def dataset_facets(self, facets_dict, dataset_type):

        facets_dict = {'extras_accessLevel': 'Access Level', 'tags': 'Keywords', 'organization': 'Organizations', 'res_format': ('File Format')}

        return facets_dict

class USMetadataPlugin(plugins.SingletonPlugin,
        tk.DefaultDatasetForm):
    '''An example IDatasetForm CKAN plugin.

    Uses a tag vocabulary to add a custom metadata field to datasets.

    '''
    plugins.implements(plugins.IConfigurer, inherit=False)
    plugins.implements(plugins.IDatasetForm, inherit=False)
    plugins.implements(plugins.ITemplateHelpers, inherit=False)

    # These record how many times methods that this plugin's methods are
    # called, for testing purposes.
    num_times_new_template_called = 0
    num_times_read_template_called = 0
    num_times_edit_template_called = 0
    num_times_comments_template_called = 0
    num_times_search_template_called = 0
    num_times_history_template_called = 0
    num_times_package_form_called = 0
    num_times_check_data_dict_called = 0
    num_times_setup_template_variables_called = 0

    def update_config(self, config):
        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        tk.add_template_directory(config, 'templates')

    def get_helpers(self):
        return {'accessLevels': accessLevels}

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    def _modify_package_schema(self, schema):
        #schema.update({
        #        'access_level': [tk.get_validator('ignore_missing'),
        #            tk.get_converter('convert_to_tags')('access_levels')]
        #        })

        # Add custom access_level as extra field
        schema.update({
                'accessLevel': [tk.get_validator('ignore_missing'),
                    tk.get_converter('convert_to_extras')]
                })

        # Add custom systemOfRecord as extra field
        schema.update({
                'systemOfRecords': [tk.get_validator('ignore_missing'),
                    tk.get_converter('convert_to_extras')]
                })

        # Add custom granularity as extra field
        schema.update({
                'granularity': [tk.get_validator('ignore_missing'),
                    tk.get_converter('convert_to_extras')]
                })


        # Add our custom_text metadata field to the schema, this one will use               
        # convert_to_extras instead of convert_to_tags.
        schema.update({
                'dataDictionary': [tk.get_validator('ignore_missing'),
                    tk.get_converter('convert_to_extras')]
                })
        return schema

    def create_package_schema(self):
        schema = super(USMetadataPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(USMetadataPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(USMetadataPlugin, self).show_package_schema()

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema['tags']['__extras'].append(tk.get_converter('free_tags_only'))

        # Add our custom access_level metadata field to the schema.
        schema.update({
            'accessLevel': [
                tk.get_converter('convert_from_tags')('accessLevels'),
                tk.get_validator('ignore_missing')]
            })

        # Add our accessLevel field to the dataset schema.
        #schema.update({
        #    'accessLevel': [tk.get_converter('convert_from_extras'),
        #        tk.get_validator('ignore_missing')]
        #    })

        # Add our dataDictionary field to the dataset schema.
        schema.update({
            'dataDictionary': [tk.get_converter('convert_from_extras'),
                tk.get_validator('ignore_missing')]
            })

       	# Add our systemOfRecords field to the dataset schema.
        schema.update({
            'systemOfRecords': [tk.get_converter('convert_from_extras'),
                tk.get_validator('ignore_missing')]
            })

        # Add our granularity field to the dataset schema.
        schema.update({
            'granularity': [tk.get_converter('convert_from_extras'),
                tk.get_validator('ignore_missing')]
            })

        return schema


    # These methods just record how many times they're called, for testing
    # purposes.
    # TODO: It might be better to test that custom templates returned by
    # these methods are actually used, not just that the methods get
    # called.

    def setup_template_variables(self, context, data_dict):
        USMetadataPlugin.num_times_setup_template_variables_called += 1
        return super(USMetadataPlugin, self).setup_template_variables(
                context, data_dict)

    def new_template(self):
        USMetadataPlugin.num_times_new_template_called += 1
        return super(USMetadataPlugin, self).new_template()

    def read_template(self):
        USMetadataPlugin.num_times_read_template_called += 1
        return super(USMetadataPlugin, self).read_template()

    def edit_template(self):
        USMetadataPlugin.num_times_edit_template_called += 1
        return super(USMetadataPlugin, self).edit_template()

    def comments_template(self):
        USMetadataPlugin.num_times_comments_template_called += 1
        return super(USMetadataPlugin, self).comments_template()

    def search_template(self):
        USMetadataPlugin.num_times_search_template_called += 1
        return super(USMetadataPlugin, self).search_template()

    def history_template(self):
        USMetadataPlugin.num_times_history_template_called += 1
        return super(USMetadataPlugin, self).history_template()

    def package_form(self):
        USMetadataPlugin.num_times_package_form_called += 1
        return super(USMetadataPlugin, self).package_form()

    # check_data_dict() is deprecated, this method is only here to test that
    # legacy support for the deprecated method works.
    def check_data_dict(self, data_dict, schema=None):
        USMetadataPlugin.num_times_check_data_dict_called += 1

