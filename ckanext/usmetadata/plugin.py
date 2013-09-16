from logging import getLogger
import ckan.plugins as p
import formencode.validators as v
import copy
#from ckan.plugins import implements, SingletonPlugin, toolkit, IConfigurer, ITemplateHelpers, IDatasetForm, IPackageController
from formencode.validators import validators

log = getLogger(__name__)

#excluded title, description, tags and last update as they're part of the default ckan dataset metadata
required_metadata = ({'id':'public_access_level', 'validators': [v.Regex(r'^([Pp]ublic)|([Rr]estricted)$')]},
                     {'id':'publisher', 'validators': [v.String(max=100)]},
                     {'id':'contact_name', 'validators': [v.String(max=100)]},
                     {'id':'contact_email', 'validators': [v.Email(),v.String(max=50)]},

                     #TODO should this unique_id be validated against any other unique IDs for this agency?
                     {'id':'unique_id', 'validators': [v.String(max=100)]}
)


#all required_metadata should be required
def get_req_metadata_for_create():
    new_req_meta = copy.copy(required_metadata)
    validator = p.toolkit.get_validator('not_empty')
    for meta in new_req_meta:
        meta['validators'].append(validator)
    return new_req_meta

def get_req_metadata_for_show_update():
    new_req_meta = copy.copy(required_metadata)
    validator = p.toolkit.get_validator('ignore_empty')
    for meta in new_req_meta:
        meta['validators'].append(validator)
    return new_req_meta

#excluded download_url, endpoint, format and license as they may be discoverable
required_if_applicable_metadata = (
     {'id':'data_dictionary', 'validators': [v.URL(),v.String(max=350)]},
     {'id':'endpoint', 'validators': [v.URL(),v.String(max=350)]},
     {'id':'spatial', 'validators': [v.String(max=500)]},
     {'id':'temporal', 'validators': [v.String(max=300)]})

for meta in required_if_applicable_metadata:
    meta['validators'].append(p.toolkit.get_validator('ignore_empty'))

#some of these could be excluded (e.g. related_documents) which can be captured from other ckan default data
expanded_metadata = ({'id': 'release_date', 'validators': [v.String(max=500)]},
                      {'id':'accrual_periodicity', 'validators': [v.Regex(r'^([Dd]aily)|([Hh]ourly)|([Ww]eekly)|([yY]early)|([oO]ther)$')]},
                      {'id':'language', 'validators': [v.String(max=500)]},
                      {'id':'granularity', 'validators': [v.String(max=500)]},
                      {'id':'data_quality', 'validators': [v.String(max=1000)]},
                      {'id':'category', 'validators': [v.String(max=1000)]},
                      {'id':'related_documents', 'validators': [v.String(max=1000)]},
                      {'id':'size', 'validators': [v.String(max=50)]},
                     {'id':'homepage_url', 'validators': [v.URL(), v.String(max=350)]},
                     {'id':'rss_feed', 'validators': [v.URL(), v.String(max=350)]},
                     {'id':'system_of_records', 'validators': [v.URL(), v.String(max=350)]},
                     {'id':'system_of_records_none_related_to_this_dataset', 'validators': [v.URL(), v.String(max=350)]}
)

for meta in expanded_metadata:
    meta['validators'].append(p.toolkit.get_validator('ignore_empty'))



schema_updates_for_create = [{meta['id'] : meta['validators']+[p.toolkit.get_converter('convert_to_extras')]} for meta in (get_req_metadata_for_create()+required_if_applicable_metadata + expanded_metadata)]
schema_updates_for_update_show = [{meta['id'] : meta['validators']+[p.toolkit.get_converter('convert_to_extras')]} for meta in (get_req_metadata_for_show_update()+required_if_applicable_metadata + expanded_metadata)]

class CommonCoreMetadataFormPlugin(p.SingletonPlugin, p.toolkit.DefaultDatasetForm):
    '''This plugin adds fields for the metadata (known as the Common Core) defined at
    https://github.com/project-open-data/project-open-data.github.io/blob/master/schema.md
    '''

    p.implements(p.ITemplateHelpers)
    p.implements(p.IConfigurer)
    p.implements(p.IDatasetForm)

    @classmethod
    def load_data_into_dict(cls, dict):
        '''
        a jinja2 template helper function.
        'extras' contains a list of dicts corresponding to the extras used to store arbitrary key value pairs in CKAN.
        This function moves each entry in 'extras' that is a common core metadata into 'common_core'

        Example:
        {'hi':'there', 'extras':[{'key': 'publisher', 'value':'USGS'}]}
        becomes
        {'hi':'there', 'common_core':{'publisher':'USGS'}, 'extras':[]}

        '''
        log.debug('load_data_into_dict called')
        common_metadata = [x['id'] for x in required_metadata+required_if_applicable_metadata+expanded_metadata]

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
            log.debug('''Expected key ['%s'] not found, attempting to move common core keys to subdictionary''', ex.message)
            #this can happen when a form fails validation, as all the data will now be as key,value pairs, not under extras,
            #so we'll move them to the expected point again to fill in the values
            # e.g.
            # { 'foo':'bar','publisher':'somename'} becomes {'foo':'bar', 'common_core':{'publisher':'somename'}}

            keys_to_remove = []

            #TODO remove debug
            log.debug('common core metadata: {0}'.format(common_metadata))
            for key,value in dict.iteritems():
                #TODO remove debug
                log.debug('checking key: {0}'.format(key))
                if key in common_metadata:
                    #TODO remove debug
                    log.debug('adding key: {0}'.format(key))
                    dict['common_core'][key]=value
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del dict[key]

        return dict

    @classmethod
    def __create_vocabulary(cls, name, *values):
        '''Create vocab and tags, if they don't exist already.
            name: the name or unique id of the vocabulary  e.g. 'flower_colors'
            values: the values that the vocabulary can take on e.g. ('blue', 'orange', 'purple', 'white', 'yellow)
        '''
        user = p.toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        context = {'user': user['name']}

        log.debug("Creating vocab '{0}'".format(name))
        data = {'name': name}
        vocab = p.toolkit.get_action('vocabulary_create')(context, data)
        log.debug('Vocab created: {0}'.format(vocab))
        for tag in values:
            log.debug(
                "Adding tag {0} to vocab {1}'".format(tag, name))
            data = {'name': tag, 'vocabulary_id': vocab['id']}
            p.toolkit.get_action('tag_create')(context, data)
        return vocab

    @classmethod
    def get_access_levels(cls):
        '''        log.debug('get_accrual_periodicity() called')
            Jinja2 template helper function, gets the vocabulary for access levels
        '''
        user = p.toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        context = {'user': user['name']}

        vocab = None
        try:
            data = {'id': 'public_access_level'} #we can use the id or name for id param
            vocab = p.toolkit.get_action('vocabulary_show')(context, data)
        except:
            log.debug("vocabulary_show failed, meaning the vocabulary for access level doesn't exist")
            vocab = cls.__create_vocabulary(u'public_access_level', u'public', u'restricted')

        access_levels = [x['display_name'] for x in vocab['tags']]
        log.debug("vocab tags: %s" % access_levels)

        return access_levels

    @classmethod
    def get_accrual_periodicity(cls):
        '''
            Jinja2 template helper function, gets the vocabulary for accrual periodicity
        '''
        user = p.toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        context = {'user': user['name']}

        vocab = None
        try:
            data = {'id': 'accrual_periodicity'} #we can use the id or name for id param
            vocab = p.toolkit.get_action('vocabulary_show')(context, data)
        except:
            log.debug("vocabulary_show failed, meaning the vocabulary for accrual periodicity doesn't exist")
            vocab = cls.__create_vocabulary('accrual_periodicity', u'hourly', u'daily', u'weekly', u'yearly', u'other')

        accrual_periodicity = [x['display_name'] for x in vocab['tags']]
        log.debug("vocab tags: %s" % accrual_periodicity)

        return accrual_periodicity
        log.debug('get_accrual_periodicity() called')

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
        #return ['dataset', 'package']
        return []

    #See ckan.plugins.interfaces.IDatasetForm
    def update_config(self, config):
        # Instruct CKAN to look in the ```templates``` directory for customized templates and snippets
        p.toolkit.add_template_directory(config, 'templates')

    #See ckan.plugins.interfaces.IDatasetForm
    def _modify_package_schema(self, schema):
        log.debug("_modify_package_schema called")

        for update in schema_updates_for_create:
            schema.update(update)

        return schema

    def _modify_package_schema_update_show(self, schema):
        log.debug("_modify_package_schema_update_show called")

        for update in schema_updates_for_update_show:
            schema.update(update)

        return schema

    #See ckan.plugins.interfaces.IDatasetForm
    def create_package_schema(self):
        log.debug('create_package_schema')
        schema = super(CommonCoreMetadataFormPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    #See ckan.plugins.interfaces.IDatasetForm
    def update_package_schema(self):
        log.debug('update_package_schema')
        schema = super(CommonCoreMetadataFormPlugin, self).update_package_schema()
#TODO uncomment, should be using schema for updates, but it's causing problems during resource creation
#        schema = self._modify_package_schema_update_show(schema)

        return schema

    #See ckan.plugins.interfaces.IDatasetForm
    def show_package_schema(self):
        log.debug('show_package_schema')
        schema = super(CommonCoreMetadataFormPlugin, self).show_package_schema()

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema['tags']['__extras'].append(p.toolkit.get_converter('free_tags_only'))

        return schema

    #Method below allows functions and other methods to be called from the Jinja template using the h variable
    def get_helpers(self):
        log.debug('get_helpers() called')
        return {'public_access_levels': self.get_access_levels, 'required_metadata': required_metadata,
                'load_data_into_dict':  self.load_data_into_dict,
                'accrual_periodicity': self.get_accrual_periodicity}