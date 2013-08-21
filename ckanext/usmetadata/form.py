from logging import getLogger
from ckan.plugins import implements, toolkit, ITemplateHelpers, SingletonPlugin, IConfigurer

log = getLogger(__name__)

def create_access_levels():
    '''Create accessLevels vocab and tags, if they don't exist already.'''
    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}
    log.debug("Creating access levels")
    try:
        data = {'id': 'accessLevels'}
        toolkit.get_action('vocabulary_show')(context, data)
        log.info("Example genre vocabulary already exists, skipping.")
    except toolkit.ObjectNotFound:
        log.info("Creating vocab 'accessLevels'")
        data = {'name': 'accessLevels'}
        vocab = toolkit.get_action('vocabulary_create')(context, data)
        for tag in (u'public', u'restricted', u'private'):
            log.info(
                "Adding tag {0} to vocab 'accessLevels'".format(tag))
            data = {'name': tag, 'vocabulary_id': vocab['id']}
            toolkit.get_action('tag_create')(context, data)

def accessLevels():
    '''Return the list of access levels from the accessLevels vocabulary.'''
    create_access_levels()
    try:
        access_levels = toolkit.get_action('tag_list')(
            data_dict={'vocabulary_id': 'accessLevels'})
        return accessLevels
    except toolkit.ObjectNotFound:
        return None

class RequiredMetadataForm(SingletonPlugin, toolkit.DefaultDatasetForm):
    '''This plugin adds required fields for metadata (known as the Common Core) as defined at
    https://github.com/project-open-data/project-open-data.github.io/blob/master/schema.md using tag vocabularies
    '''

    implements(ITemplateHelpers, inherit=False)
#    implements(IConfigurer, inherit=True)

    def _modify_package_schema(self, schema):
        #TODO need to modify the package schema
        #schema.update({
        #        'access_level': [toolkit.get_validator('ignore_missing'),
        #            toolkit.get_converter('convert_to_tags')('access_levels')]
        #        })

        # Add custom access_level as extra field
        schema.update({
            'accessLevel': [toolkit.get_validator('ignore_missing'),
                            toolkit.get_converter('convert_to_extras')]
        })

        # Add custom systemOfRecord as extra field
        schema.update({
            'systemOfRecords': [toolkit.get_validator('ignore_missing'),
                                toolkit.get_converter('convert_to_extras')]
        })

        # Add custom granularity as extra field
        schema.update({
            'granularity': [toolkit.get_validator('ignore_missing'),
                            toolkit.get_converter('convert_to_extras')]
        })


        # Add our custom_text metadata field to the schema, this one will use
        # convert_to_extras instead of convert_to_tags.
        schema.update({
            'dataDictionary': [toolkit.get_validator('ignore_missing'),
                               toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def create_package_schema(self):
        schema = super(RequiredMetadataForm, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(RequiredMetadataForm, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(RequiredMetadataForm, self).show_package_schema()

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))

        # Add our custom access_level metadata field to the schema.
        schema.update({
            'accessLevel': [
                toolkit.get_converter('convert_from_tags')('accessLevels'),
                toolkit.get_validator('ignore_missing')]
        })

        # Add our accessLevel field to the dataset schema.
        #schema.update({
        #    'accessLevel': [toolkit.get_converter('convert_from_extras'),
        #        toolkit.get_validator('ignore_missing')]
        #    })

        # Add our dataDictionary field to the dataset schema.
        schema.update({
            'dataDictionary': [toolkit.get_converter('convert_from_extras'),
                               toolkit.get_validator('ignore_missing')]
        })

        # Add our systemOfRecords field to the dataset schema.
        schema.update({
            'systemOfRecords': [toolkit.get_converter('convert_from_extras'),
                                toolkit.get_validator('ignore_missing')]
        })

        # Add our granularity field to the dataset schema.
        schema.update({
            'granularity': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })

    def get_helpers(self):
        return {'accessLevels': accessLevels}
