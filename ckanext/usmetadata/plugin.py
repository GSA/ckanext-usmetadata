from logging import getLogger
import ckan.plugins as p
#from ckan.plugins import implements, SingletonPlugin, toolkit, IConfigurer, ITemplateHelpers, IDatasetForm, IPackageController

log = getLogger(__name__)

#Jinja template helper functions
def _create_access_level_vocabulary():
    '''Create accessLevels vocab and tags, if they don't exist already.'''
    user = p.toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}

    log.debug("Creating vocab 'public_access_levels'")
    data = {'name': 'public_access_level'}
    vocab = p.toolkit.get_action('vocabulary_create')(context, data)
    log.debug('Vocab created: %s' % vocab)
    for tag in (u'public', u'restricted'):
        log.debug(
            "Adding tag {0} to vocab 'public_access_levels'".format(tag))
        data = {'name': tag, 'vocabulary_id': vocab['id']}
        p.toolkit.get_action('tag_create')(context, data)
    return vocab

def get_access_levels():
    log.debug('get_access_levels() called')

    user = p.toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}

    vocab = None
    try:
        data = {'id': 'public_access_level'} #we can use the id or name for id param
        vocab = p.toolkit.get_action('vocabulary_show')(context, data)
    except:
        log.debug("vocabulary_show failed, meaning the vocabulary for access level doesn't exist")
        vocab = _create_access_level_vocabulary()

    access_levels = [x['display_name'] for x in vocab['tags']]
    log.debug("vocab tags: %s" % access_levels)

    return access_levels

def _create_accrual_periodicity_vocabulary():
    '''Create accessLevels vocab and tags, if they don't exist already.'''
    user = p.toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}

    log.debug("Creating vocab 'accrual_periodicity'")
    data = {'name': 'accrual_periodicity'}
    vocab = p.toolkit.get_action('vocabulary_create')(context, data)
    log.debug('Vocab created: %s' % vocab)
    for tag in (u'hourly', u'daily', u'weekly', u'yearly', u'other'):
        log.debug(
            "Adding tag {0} to vocab 'accrual_periodicity'".format(tag))
        data = {'name': tag, 'vocabulary_id': vocab['id']}
        p.toolkit.get_action('tag_create')(context, data)
    return vocab

def get_accrual_periodicity():
    log.debug('get_accrual_periodicity() called')

    user = p.toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}

    vocab = None
    try:
        data = {'id': 'accrual_periodicity'} #we can use the id or name for id param
        vocab = p.toolkit.get_action('vocabulary_show')(context, data)
    except:
        log.debug("vocabulary_show failed, meaning the vocabulary for accrual periodicity doesn't exist")
        vocab = _create_accrual_periodicity_vocabulary()

    accrual_periodicity = [x['display_name'] for x in vocab['tags']]
    log.debug("vocab tags: %s" % accrual_periodicity)

    return accrual_periodicity

#excluded title, description, tags and last update as they're part of the default ckan dataset metadata
required_metadata = ['public_access_level', 'publisher', 'contact_name', 'contact_email', 'unique_id']

#excluded download_url, endpoint, format and license as they may be discoverable
required_if_applicable_metadata = ['data_dictionary', 'endpoint', 'spatial', 'temporal']

#some of these could be excluded (e.g. related_documents) which can be captured from other ckan default data
expanded_metadata = ['release_date', 'accrual_periodicity', 'language', 'granularity', 'data_quality', 'category',
                     'related_documents', 'size', 'homepage_url', 'rss_feed', 'system_of_records',
                     'system_of_records_none_related_to_this_dataset']

def _load_data_into_dict(dict):
    '''
    extras contains a list of dicts corresponding to the extras used to store arbitrary key value pairs in CKAN.
    This function moves each entry in 'extras' that is a common core metadata into 'common_core'

    Example:
    {'hi':'there', 'extras':[{'key': 'publisher', 'value':'USGS'}]}
    becomes
    {'hi':'there', 'common_core':{'publisher':'USGS'}, 'extras':[]}

    '''
    common_metadata = required_metadata+required_if_applicable_metadata+expanded_metadata

    try:
        dict['common_core']
    except KeyError:
        dict['common_core'] = {}

    reduced_extras = []

    try:
        for extra in dict['extras']:

            if extra['key'] in common_metadata:
                dict['common_core'][extra['key']]=extra['value']
            else:
                reduced_extras.append(extra)

        dict['extras'] = reduced_extras
    except KeyError as ex:
        log.warn('''Assumption violation: expected key ['%s'] not found, returning original dict''', ex.message)

    return dict

class CommonCoreMetadataForm(p.SingletonPlugin, p.toolkit.DefaultDatasetForm):
    '''This plugin adds fields for the metadata (known as the Common Core) defined at
    https://github.com/project-open-data/project-open-data.github.io/blob/master/schema.md
    '''

    p.implements(p.ITemplateHelpers)
    p.implements(p.IConfigurer)
    p.implements(p.IDatasetForm)

    #See ckan.plugins.interfaces.IDatasetForm
    def is_fallback(self):
        # Return True so that we use the extension's dataset form instead of CKAN's default for
        # /dataset/new and /dataset/edit
        return True

    #See ckan.plugins.interfaces.IDatasetForm
    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        #
        return ['dataset', 'package']

    #See ckan.plugins.interfaces.IDatasetForm
    def update_config(self, config):
        # Instruct CKAN to look in the ```templates``` directory for customized templates and snippets
        p.toolkit.add_template_directory(config, 'templates')

    #See ckan.plugins.interfaces.IDatasetForm
    def _modify_package_schema(self, schema):
        log.debug("_modify_package_schema called")
        #TODO change ignore_missing to something requiring the fields to be populated
        for metadata in required_metadata:
            schema.update({
                metadata: [p.toolkit.get_validator('ignore_missing'),
                           p.toolkit.get_converter('convert_to_extras')]
            })

        for metadata in (required_if_applicable_metadata + expanded_metadata):
            schema.update({
                metadata: [p.toolkit.get_validator('ignore_missing'),
                           p.toolkit.get_converter('convert_to_extras')]
            })

        return schema

    #See ckan.plugins.interfaces.IDatasetForm
    def create_package_schema(self):
        log.debug("create_package_schema called")
        schema = super(CommonCoreMetadataForm, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    #See ckan.plugins.interfaces.IDatasetForm
    def update_package_schema(self):
        log.debug("update_package_schema called")
        schema = super(CommonCoreMetadataForm, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    #See ckan.plugins.interfaces.IDatasetForm
    def show_package_schema(self):
        log.debug("show_package_schema called")
        schema = super(CommonCoreMetadataForm, self).show_package_schema()

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema['tags']['__extras'].append(p.toolkit.get_converter('free_tags_only'))

        #TODO does the schema NEED to be modified every time it is shown?
        schema = self._modify_package_schema(schema)
        return schema

    #See ckan.plugins.interfaces.IDatasetForm
    def setup_template_variables(self, context, data_dict):
        log.debug('setup_template_variables() called')
        #TODO replace below with actual variables to be passed to template
        common_metadata = common_metadata = required_metadata+required_if_applicable_metadata+expanded_metadata
        meta_dict = {}
        for meta in common_metadata:
            meta_dict[meta]='foo'+meta
        p.toolkit.c.common_core = meta_dict

    #Method below allows functions and other methods to be called from the Jinja template using the h variable
    def get_helpers(self):
        log.debug('get_helpers() called')
        return {'public_access_levels': get_access_levels, 'required_metadata': required_metadata,
                'load_data_into_dict':_load_data_into_dict,
                'accrual_periodicity': get_accrual_periodicity}