from logging import getLogger
import ckan.plugins as p
import formencode.validators as v
from pylons import request, response
import copy
import json
import os
from ckan.lib.base import BaseController
#from ckan.plugins import implements, SingletonPlugin, toolkit, IConfigurer, ITemplateHelpers, IDatasetForm, IPackageController
from formencode.validators import validators

log = getLogger(__name__)

#excluded title, description, tags and last update as they're part of the default ckan dataset metadata
required_metadata = ({'id':'title', 'validators': [v.String(max=300)]},
                     {'id':'notes', 'validators': [v.NotEmpty]},
                     {'id':'tag_string', 'validators': [v.NotEmpty]},
                     {'id':'public_access_level', 'validators': [v.Regex(r'^([Pp]ublic)|([Rr]estricted [Pp]ublic)|([Pp]rivate)|([nN]on-public)$')]},
                     {'id':'publisher', 'validators': [v.String(max=300)]},
                     {'id':'contact_name', 'validators': [v.String(max=300)]},
                     {'id':'contact_email', 'validators': [v.Email(),v.String(max=100)]},

                     #TODO should this unique_id be validated against any other unique IDs for this agency?
                     {'id':'unique_id', 'validators': [v.String(max=100)]}
)

required_metadata_update = ({'id':'public_access_level','validators': [v.Regex(r'^([Pp]ublic)|([Rr]estricted [Pp]ublic)|([Pp]rivate)|([nN]on-public)$')]},
                            {'id':'publisher', 'validators': [v.String(max=300)]},
                            {'id':'contact_name', 'validators': [v.String(max=300)]},
                            {'id':'contact_email', 'validators': [v.Email(),v.String(max=100)]},

                            #TODO should this unique_id be validated against any other unique IDs for this agency?
                            {'id':'unique_id', 'validators': [v.String(max=100)]}
)

accrual_periodicity = [u"Annual", u"Bimonthly", u"Semiweekly", u"Daily", u"Biweekly", u"Semiannual", u"Biennial", u"Triennial",
                u"Three times a week", u"Three times a month", u"Continuously updated", u"Monthly", u"Quarterly", u"Semimonthly",
                u"Three times a year", u"Weekly", u"Completely irregular"]

access_levels = ['public', 'restricted public', 'non-public']

# Dictionary of all media types
media_types = json.loads(open(os.path.join(os.path.dirname(__file__), 'media_types.json'), 'r').read())

#all required_metadata should be required
def get_req_metadata_for_create():
    log.debug('get_req_metadata_for_create')
    new_req_meta = copy.copy(required_metadata)
    validator = p.toolkit.get_validator('not_empty')
    for meta in new_req_meta:
        meta['validators'].append(validator)
    return new_req_meta

def get_req_metadata_for_update():
    log.debug('get_req_metadata_for_update')
    new_req_meta = copy.copy(required_metadata_update)
    validator = p.toolkit.get_validator('ignore_missing')
    for meta in new_req_meta:
        meta['validators'].append(validator)
    return new_req_meta

def get_req_metadata_for_show_update():
    new_req_meta = copy.copy(required_metadata)
    validator = p.toolkit.get_validator('ignore_missing')
    for meta in new_req_meta:
        meta['validators'].append(validator)
    return new_req_meta

#excluded download_url, endpoint, format and license as they may be discoverable
required_if_applicable_metadata = (
     {'id':'data_dictionary', 'validators': [v.URL(),v.String(max=350)]},
     {'id':'endpoint', 'validators': [v.URL(),v.String(max=350)]},
     {'id':'spatial', 'validators': [v.String(max=500)]},
     {'id':'temporal', 'validators': [v.Regex(r"^([0-9]{4})(-([0-9]{1,2})(-([0-9]{1,2})((.)([0-9]{2}):([0-9]{2})(:([0-9]{2})(\.([0-9]+))?)?(Z|(([-+])([0-9]{2}):([0-9]{2})))?)?)?)?(/([0-9]{4})(-([0-9]{1,2})(-([0-9]{1,2})((.)([0-9]{2}):([0-9]{2})(:([0-9]{2})(\.([0-9]+))?)?(Z|(([-+])([0-9]{2}):([0-9]{2})))?)?)?)?){0,1}$")]},
     {'id':'bureau_code', 'validators': [v.Regex(r'^\d{3}:\d{2}(\s*,\s*\d{3}:\d{2}\s*)*$')]},
     {'id':'program_code', 'validators': [v.Regex(r'^\d{3}:\d{3}(\s*,\s*\d{3}:\d{3}\s*)*$')]},
     {'id':'access_level_comment', 'validators': [v.String(max=255)]},
)

for meta in required_if_applicable_metadata:
    meta['validators'].append(p.toolkit.get_validator('ignore_empty'))

#some of these could be excluded (e.g. related_documents) which can be captured from other ckan default data
expanded_metadata = ({'id': 'release_date', 'validators': [v.String(max=500)]},
                      {'id':'accrual_periodicity', 'validators': [v.Regex(r'^([Aa]nnual)|([Bb]imonthly)|([Ss]emiweekly)|([Dd]aily)|([Bb]iweekly)|([Ss]emiannual)|([Bb]iennial)|([Tt]riennial)|(Three times a week)|(Three times a month)|(Continuously updated)|([Mm]onthly)|([Qq]uarterly)|([Ss]emimonthly)|(Three times a year)|(Weekly)|(Completely irregular)$')]},
                      {'id':'language', 'validators': [v.Regex(r"^(((([A-Za-z]{2,3}(-([A-Za-z]{3}(-[A-Za-z]{3}){0,2}))?)|[A-Za-z]{4}|[A-Za-z]{5,8})(-([A-Za-z]{4}))?(-([A-Za-z]{2}|[0-9]{3}))?(-([A-Za-z0-9]{5,8}|[0-9][A-Za-z0-9]{3}))*(-([0-9A-WY-Za-wy-z](-[A-Za-z0-9]{2,8})+))*(-(x(-[A-Za-z0-9]{1,8})+))?)|(x(-[A-Za-z0-9]{1,8})+)|((en-GB-oed|i-ami|i-bnn|i-default|i-enochian|i-hak|i-klingon|i-lux|i-mingo|i-navajo|i-pwn|i-tao|i-tay|i-tsu|sgn-BE-FR|sgn-BE-NL|sgn-CH-DE)|(art-lojban|cel-gaulish|no-bok|no-nyn|zh-guoyu|zh-hakka|zh-min|zh-min-nan|zh-xiang)))(\s*,\s*(((([A-Za-z]{2,3}(-([A-Za-z]{3}(-[A-Za-z]{3}){0,2}))?)|[A-Za-z]{4}|[A-Za-z]{5,8})(-([A-Za-z]{4}))?(-([A-Za-z]{2}|[0-9]{3}))?(-([A-Za-z0-9]{5,8}|[0-9][A-Za-z0-9]{3}))*(-([0-9A-WY-Za-wy-z](-[A-Za-z0-9]{2,8})+))*(-(x(-[A-Za-z0-9]{1,8})+))?)|(x(-[A-Za-z0-9]{1,8})+)|((en-GB-oed|i-ami|i-bnn|i-default|i-enochian|i-hak|i-klingon|i-lux|i-mingo|i-navajo|i-pwn|i-tao|i-tay|i-tsu|sgn-BE-FR|sgn-BE-NL|sgn-CH-DE)|(art-lojban|cel-gaulish|no-bok|no-nyn|zh-guoyu|zh-hakka|zh-min|zh-min-nan|zh-xiang)))\s*)*$")]},
                      {'id':'data_quality', 'validators': [v.String(max=1000)]},
                      {'id':'category', 'validators': [v.String(max=1000)]},
                      {'id':'related_documents', 'validators': [v.String(max=1000)]},
                     {'id':'homepage_url', 'validators': [v.URL(), v.String(max=350)]},
                     {'id':'rss_feed', 'validators': [v.URL(), v.String(max=350)]},
                     {'id':'system_of_records', 'validators': [v.URL(), v.String(max=350)]},
                     {'id':'system_of_records_none_related_to_this_dataset', 'validators': [v.URL(), v.String(max=350)]},
                     {'id':'primary_it_investment_uii', 'validators': [v.String(max=75)]},
                     {'id':'modified', 'validators': [v.DateValidator(),v.String(max=10)]}
)

for meta in expanded_metadata:
    meta['validators'].append(p.toolkit.get_validator('ignore_empty'))



schema_updates_for_create = [{meta['id'] : meta['validators']+[p.toolkit.get_converter('convert_to_extras')]} for meta in (get_req_metadata_for_create()+required_if_applicable_metadata + expanded_metadata)]
schema_updates_for_update = [{meta['id'] : meta['validators']+[p.toolkit.get_converter('convert_to_extras')]} for meta in (get_req_metadata_for_update()+required_if_applicable_metadata + expanded_metadata)]
schema_updates_for_show = [{meta['id'] : meta['validators']+[p.toolkit.get_converter('convert_from_extras')]} for meta in (get_req_metadata_for_show_update()+required_if_applicable_metadata + expanded_metadata)]


class CommonCoreMetadataFormPlugin(p.SingletonPlugin, p.toolkit.DefaultDatasetForm):
    '''This plugin adds fields for the metadata (known as the Common Core) defined at
    https://github.com/project-open-data/project-open-data.github.io/blob/master/schema.md
    '''

    p.implements(p.ITemplateHelpers, inherit=False)
    p.implements(p.IConfigurer, inherit=False)
    p.implements(p.IDatasetForm, inherit=False)
    p.implements(p.interfaces.IRoutes, inherit=True)

    def after_map(selfself, m):
        m.connect('media_type', '/api/2/util/resource/media_autocomplete', controller='ckanext.usmetadata.plugin:MediaController', action='get_media_types')
        return m

    @classmethod
    def load_data_into_dict(cls, data_dict):
        '''
        a jinja2 template helper function.
        'extras' contains a list of dicts corresponding to the extras used to store arbitrary key value pairs in CKAN.
        This function moves each entry in 'extras' that is a common core metadata into 'common_core'

        Example:
        {'hi':'there', 'extras':[{'key': 'publisher', 'value':'USGS'}]}
        becomes
        {'hi':'there', 'common_core':{'publisher':'USGS'}, 'extras':[]}

        '''

        new_dict = data_dict.copy()
        common_metadata = [x['id'] for x in required_metadata+required_if_applicable_metadata+expanded_metadata]

        try:
            new_dict['common_core']
        except KeyError:
            new_dict['common_core'] = {}

        reduced_extras = []

        try:
            for extra in new_dict['extras']:

                if extra['key'] in common_metadata:
                    new_dict['common_core'][extra['key']]=extra['value']
                else:
                    reduced_extras.append(extra)

            new_dict['extras'] = reduced_extras
        except KeyError as ex:
            log.debug('''Expected key ['%s'] not found, attempting to move common core keys to subdictionary''', ex.message)
            #this can happen when a form fails validation, as all the data will now be as key,value pairs, not under extras,
            #so we'll move them to the expected point again to fill in the values
            # e.g.
            # { 'foo':'bar','publisher':'somename'} becomes {'foo':'bar', 'common_core':{'publisher':'somename'}}

            keys_to_remove = []

            #TODO remove debug
            log.debug('common core metadata: {0}'.format(common_metadata))
            for key,value in new_dict.iteritems():
                #TODO remove debug
                log.debug('checking key: {0}'.format(key))
                if key in common_metadata:
                    #TODO remove debug
                    log.debug('adding key: {0}'.format(key))
                    new_dict['common_core'][key]=value
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del new_dict[key]

        return new_dict

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

        # Register this plugin's fanstatic directory with CKAN.
        # Here, 'fanstatic' is the path to the fanstatic directory
        # (relative to this plugin.py file), and 'example_theme' is the name
        # that we'll use to refer to this fanstatic directory from CKAN
        # templates.
        p.toolkit.add_resource('fanstatic', 'dataset_url')

    #See ckan.plugins.interfaces.IDatasetForm
    def _create_package_schema(self, schema):
        log.debug("_create_package_schema called")

        for update in schema_updates_for_create:
            schema.update(update)

        return schema

    def _modify_package_schema_update(self, schema):
        log.debug("_modify_package_schema_update called")

        for update in schema_updates_for_update:
            schema.update(update)

        return schema

    def _modify_package_schema_show(self, schema):
        log.debug("_modify_package_schema_update_show called")

        for update in schema_updates_for_show:
            schema.update(update)

        return schema

    #See ckan.plugins.interfaces.IDatasetForm
    def create_package_schema(self):
        schema = super(CommonCoreMetadataFormPlugin, self).create_package_schema()
        schema = self._create_package_schema(schema)
        return schema

    #See ckan.plugins.interfaces.IDatasetForm
    def update_package_schema(self):
        log.debug('update_package_schema')
        schema = super(CommonCoreMetadataFormPlugin, self).update_package_schema()
        #TODO uncomment, should be using schema for updates, but it's causing problems during resource creation
        log.debug(request.path);
        #TODO: Remove this is HACK - Add validation for update only.
        if request.path.startswith('/dataset/edit'):
            schema = self._create_package_schema(schema)
        else:
            schema = self._modify_package_schema_update(schema)

        return schema

    #See ckan.plugins.interfaces.IDatasetForm
    def show_package_schema(self):
        log.debug('show_package_schema')
        schema = super(CommonCoreMetadataFormPlugin, self).show_package_schema()

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema['tags']['__extras'].append(p.toolkit.get_converter('free_tags_only'))

        schema = self._modify_package_schema_show(schema)
        return schema

    #Method below allows functions and other methods to be called from the Jinja template using the h variable
    # always_private hides Visibility selector, essentially meaning that all datasets are private to an organization
    def get_helpers(self):
        log.debug('get_helpers() called')
        return {'public_access_levels': access_levels, 'required_metadata': required_metadata,
                'load_data_into_dict':  self.load_data_into_dict,
                'accrual_periodicity': accrual_periodicity,
                'always_private': True}

class MediaController(BaseController):
    """Controller to return the acceptable media types as JSON, powering the front end"""

    def get_media_types(self):
                # set content type (charset required or pylons throws an error)
        q = request.params.get('incomplete', '')

        response.content_type = 'application/json; charset=UTF-8'

        retval = []

        for dict in media_types:
            if q in dict['media_type'] or q in dict['name'] or q in dict['ext']:
                retval.append(dict['media_type'])
            if len(retval) >= 50:
                break

        return json.dumps({'ResultSet':{'Result':retval}})
