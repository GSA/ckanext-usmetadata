import logging

from ckan.plugins import implements, SingletonPlugin, toolkit, IConfigurer, IDatasetForm, ITemplateHelpers, IFacets

# class IFacetPlugin(SingletonPlugin):
#     implements(IFacets, inherit=True)
#
#     def dataset_facets(self, facets_dict, dataset_type):
#         facets_dict = {'extras_accessLevel': 'Access Level', 'tags': 'Keywords', 'organization': 'Organizations',
#                        'res_format': ('File Format')}
#
#         return facets_dict

#TODO is this class needed at all?
class USMetadataPlugin(SingletonPlugin):

    implements(IConfigurer, inherit=False)

    def update_config(self, config):
        # Instruct CKAN to look in the ```templates``` directory for customized templates and snippets
        toolkit.add_template_directory(config, 'templates')

    # def is_fallback(self):
    #     # Return True so that we use the extension's dataset form instead of CKAN's default for
    #     # /dataset/new and /dataset/edit
    #     return True
    #
    # def package_types(self):
    #     # This plugin doesn't handle any special package types, it just
    #     # registers itself as the default (above).
    #     #
    #     return []