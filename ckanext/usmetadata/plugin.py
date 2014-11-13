import formencode.validators as v
import copy
import os
import cgi
import ckan.logic as logic
import ckan.lib.base as base
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.model as model
import ckan.plugins as p
import db_utils

from logging import getLogger
from ckan.lib.base import BaseController
from pylons import config
from ckan.common import OrderedDict, _, json, request, c, g, response

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
flatten_to_string_key = logic.flatten_to_string_key

import ckan.lib.helpers as h
#from ckan.plugins import implements, SingletonPlugin, toolkit, IConfigurer, ITemplateHelpers, IDatasetForm, IPackageController
from formencode.validators import validators

redirect = base.redirect
log = getLogger(__name__)

#excluded title, description, tags and last update as they're part of the default ckan dataset metadata
required_metadata = (
    {'id': 'title', 'validators': [p.toolkit.get_validator('not_empty'), unicode]},
    {'id': 'notes', 'validators': [p.toolkit.get_validator('not_empty'), unicode]},
    #{'id':'tag_string', 'validators': [v.NotEmpty]},
    {'id': 'public_access_level',
     'validators': [v.Regex(r'^([Pp]ublic)|([Rr]estricted [Pp]ublic)|([Pp]rivate)|([nN]on-public)$')]},
    {'id': 'publisher', 'validators': [p.toolkit.get_validator('not_empty'), unicode]},
    {'id': 'contact_name', 'validators': [p.toolkit.get_validator('not_empty'), unicode]},
    {'id': 'contact_email', 'validators': [v.Email(), v.String(max=100)]},
    #TODO should this unique_id be validated against any other unique IDs for this agency?
    {'id': 'unique_id', 'validators': [p.toolkit.get_validator('not_empty'), unicode]}
)

#used to bypass validation on create
required_metadata_update = (
    {'id': 'public_access_level',
     'validators': [v.Regex(r'^([Pp]ublic)|([Rr]estricted [Pp]ublic)|([Pp]rivate)|([nN]on-public)$')]},
    {'id': 'publisher', 'validators': [v.String(max=300)]},
    {'id': 'contact_name', 'validators': [v.String(max=300)]},
    {'id': 'contact_email', 'validators': [v.Email(), v.String(max=100)]},
    #TODO should this unique_id be validated against any other unique IDs for this agency?
    {'id': 'unique_id', 'validators': [v.String(max=100)]}
)

#some of these could be excluded (e.g. related_documents) which can be captured from other ckan default data
expanded_metadata = (
    {'id': 'release_date', 'validators': [v.String(max=500)]},
    {'id': 'accrual_periodicity', 'validators': [v.Regex(
        r'^([Aa]nnual)|([Bb]imonthly)|([Ss]emiweekly)|([Dd]aily)|([Bb]iweekly)|([Ss]emiannual)|([Bb]iennial)|([Tt]riennial)|(Three times a week)|(Three times a month)|(Continuously updated)|([Mm]onthly)|([Qq]uarterly)|([Ss]emimonthly)|(Three times a year)|(Weekly)|(Completely irregular)$')]},
    {'id': 'language', 'validators': [v.Regex(
        r"^(((([A-Za-z]{2,3}(-([A-Za-z]{3}(-[A-Za-z]{3}){0,2}))?)|[A-Za-z]{4}|[A-Za-z]{5,8})(-([A-Za-z]{4}))?(-([A-Za-z]{2}|[0-9]{3}))?(-([A-Za-z0-9]{5,8}|[0-9][A-Za-z0-9]{3}))*(-([0-9A-WY-Za-wy-z](-[A-Za-z0-9]{2,8})+))*(-(x(-[A-Za-z0-9]{1,8})+))?)|(x(-[A-Za-z0-9]{1,8})+)|((en-GB-oed|i-ami|i-bnn|i-default|i-enochian|i-hak|i-klingon|i-lux|i-mingo|i-navajo|i-pwn|i-tao|i-tay|i-tsu|sgn-BE-FR|sgn-BE-NL|sgn-CH-DE)|(art-lojban|cel-gaulish|no-bok|no-nyn|zh-guoyu|zh-hakka|zh-min|zh-min-nan|zh-xiang)))(\s*,\s*(((([A-Za-z]{2,3}(-([A-Za-z]{3}(-[A-Za-z]{3}){0,2}))?)|[A-Za-z]{4}|[A-Za-z]{5,8})(-([A-Za-z]{4}))?(-([A-Za-z]{2}|[0-9]{3}))?(-([A-Za-z0-9]{5,8}|[0-9][A-Za-z0-9]{3}))*(-([0-9A-WY-Za-wy-z](-[A-Za-z0-9]{2,8})+))*(-(x(-[A-Za-z0-9]{1,8})+))?)|(x(-[A-Za-z0-9]{1,8})+)|((en-GB-oed|i-ami|i-bnn|i-default|i-enochian|i-hak|i-klingon|i-lux|i-mingo|i-navajo|i-pwn|i-tao|i-tay|i-tsu|sgn-BE-FR|sgn-BE-NL|sgn-CH-DE)|(art-lojban|cel-gaulish|no-bok|no-nyn|zh-guoyu|zh-hakka|zh-min|zh-min-nan|zh-xiang)))\s*)*$")]},
    {'id': 'data_quality', 'validators': [v.String(max=1000)]},
    {'id': 'is_parent', 'validators': [v.String(max=1000)]},
    {'id': 'parent_dataset', 'validators': [v.String(max=1000)]},
    {'id': 'category', 'validators': [v.String(max=1000)]},
    {'id': 'related_documents', 'validators': [v.String(max=2100)]},
    {'id': 'homepage_url', 'validators': [v.String(max=2100)]},
    {'id': 'rss_feed', 'validators': [v.String(max=2100)]},
    {'id': 'system_of_records', 'validators': [v.String(max=2100)]},
    {'id': 'system_of_records_none_related_to_this_dataset', 'validators': [v.String(max=2100)]},
    {'id': 'primary_it_investment_uii', 'validators': [v.String(max=75)]},
    {'id': 'webservice', 'validators': [v.Regex(r"^(http(?:s)?\:\/\/[a-zA-Z0-9\-]+(?:\.[a-zA-Z0-9\-]+)*\.[a-zA-Z]{2,6}(?:\/?|(?:\/[\w\-]+)*)(?:\/?|\/\w+\.[a-zA-Z]{2,4}(?:\?[\w]+\=[\w\-]+)?)?(?:\&[\w]+\=[\w\-]+)*)$")]},
)

#excluded download_url, endpoint, format and license as they may be discoverable
required_if_applicable_metadata = (
    {'id': 'data_dictionary', 'validators': [v.String(max=2100)]},
    {'id': 'endpoint', 'validators': [v.String(max=2100)]},
    {'id': 'spatial', 'validators': [v.String(max=500)]},
    {'id': 'temporal', 'validators': [v.Regex(
        r"^([0-9]{4})(-([0-9]{1,2})(-([0-9]{1,2})((.)([0-9]{2}):([0-9]{2})(:([0-9]{2})(\.([0-9]+))?)?(Z|(([-+])([0-9]{2}):([0-9]{2})))?)?)?)?(/([0-9]{4})(-([0-9]{1,2})(-([0-9]{1,2})((.)([0-9]{2}):([0-9]{2})(:([0-9]{2})(\.([0-9]+))?)?(Z|(([-+])([0-9]{2}):([0-9]{2})))?)?)?)?){0,1}$")]},
    {'id': 'bureau_code', 'validators': [v.Regex(r'^\d{3}:\d{2}(\s*,\s*\d{3}:\d{2}\s*)*$')]},
    {'id': 'program_code', 'validators': [v.Regex(r'^\d{3}:\d{3}(\s*,\s*\d{3}:\d{3}\s*)*$')]},
    {'id': 'access_level_comment', 'validators': [v.String(max=255)]},
    {'id': 'modified', 'validators': [v.DateValidator(), v.String(max=50)]},
)

accrual_periodicity = [u"Annual", u"Bimonthly", u"Semiweekly", u"Daily", u"Biweekly", u"Semiannual", u"Biennial",
                       u"Triennial",
                       u"Three times a week", u"Three times a month", u"Continuously updated", u"Monthly", u"Quarterly",
                       u"Semimonthly",
                       u"Three times a year", u"Weekly", u"Completely irregular"]

access_levels = ['public', 'restricted public', 'non-public']

data_quality_options = {'': '', 'true': 'Yes', 'false': 'No'}
is_parent_options = {'true': 'Yes', 'false': 'No'}

#Used to display user-friendly labels on dataset page
dataset_labels = {
    'public_access_level': 'Public Access Level',
    'tag_string': 'Tags',
    'access_level_comment': 'Access Level Comment',
    'contact_name': 'Contact Name',
    'category': 'Category',
    'title': 'Title',
    'temporal': 'Temporal',
    'program_code': 'Program Code',
    'spatial': 'Spatial',
    'license_id': 'License',
    'bureau_code': 'Bureau Code',
    'tags': 'Tags',
    'contact_email': 'Contact Email',
    'publisher': 'Publisher',
    'name': 'Name',
    'language': 'Language',
    'accrual_periodicity': 'Frequency',
    'notes': 'Description',
    'modified': 'Last Update',
    'related_documents': 'Related Documents',
    'data_dictionary': 'Data Dictionary',
    'homepage_url': 'Homepage Url',
    'unique_id': 'Unique Identifier',
    'system_of_records': 'System of Records',
    'release_date': 'Release Date',
    'data_quality': 'Meets the agency Information Quality Guidelines',
    'primary_it_investment_uii': 'Primary IT Investment UII',
    'accessURL': 'Download URL',
    'webService': 'Endpoint',
    'format': 'Format',
    'webservice' : 'Webservice',
    'is_parent' : 'Is parent dataset',
    'parent_dataset' : 'Parent dataset'
}

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


#used to bypass validation on create
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


for meta in required_if_applicable_metadata:
    meta['validators'].append(p.toolkit.get_validator('ignore_empty'))

for meta in expanded_metadata:
    meta['validators'].append(p.toolkit.get_validator('ignore_empty'))

schema_updates_for_create = [{meta['id']: meta['validators'] + [p.toolkit.get_converter('convert_to_extras')]} for meta
                             in (get_req_metadata_for_create() + required_if_applicable_metadata + expanded_metadata)]
schema_updates_for_update = [{meta['id']: meta['validators'] + [p.toolkit.get_converter('convert_to_extras')]} for meta
                             in (get_req_metadata_for_update() + required_if_applicable_metadata + expanded_metadata)]
schema_updates_for_show = [{meta['id']: meta['validators'] + [p.toolkit.get_converter('convert_from_extras')]} for meta
                           in
                           (get_req_metadata_for_show_update() + required_if_applicable_metadata + expanded_metadata)]

class UsmetadataController(BaseController):
    def get_package_info_usmetadata(self, id, context, errors, error_summary):
        data = get_action('package_show')(context, {'id': id})
        data_dict = get_action('package_show')(context, {'id': id})
        data_dict['id'] = id
        data_dict['state'] = 'active'
        context['allow_state_change'] = True
        try:
            get_action('package_update')(context, data_dict)
        except ValidationError, e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.new_metadata(id, data, errors, error_summary)
        except NotAuthorized:
            abort(401, _('Unauthorized to update dataset'))
        redirect(h.url_for(controller='package',
                                 action='read', id=id))
        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors, 'error_summary': error_summary}
        vars['pkg_name'] = id
        return vars

    def new_resource_usmetadata(self, id, data=None, errors=None, error_summary=None):
        ''' FIXME: This is a temporary action to allow styling of the
        forms. '''
        if request.method == 'POST' and not data:
            save_action = request.params.get('save')
            data = data or clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(
                request.POST))))
            # we don't want to include save as it is part of the form
            del data['save']
            resource_id = data['id']
            del data['id']
            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author, 'auth_user_obj': c.userobj}
            # see if we have any data that we are trying to save
            data_provided = False
            for key, value in data.iteritems():
                if ((value or isinstance(value, cgi.FieldStorage))
                    and key != 'resource_type'):
                    data_provided = True
                    break
            if not data_provided and save_action != "go-dataset-complete":
                if save_action == 'go-dataset':
                    # go to final stage of adddataset
                    redirect(h.url_for(controller='package',
                                       action='edit', id=id))
                # see if we have added any resources
                try:
                    data_dict = get_action('package_show')(context, {'id': id})
                except NotAuthorized:
                    abort(401, _('Unauthorized to update dataset'))
                except NotFound:
                    abort(404,
                      _('The dataset {id} could not be found.').format(id=id))
                if str.lower(config.get('ckan.package.resource_required', 'true')) == 'true' and not len(data_dict['resources']):
                    # no data so keep on page
                    msg = _('You must add at least one data resource')
                    # On new templates do not use flash message
                    if g.legacy_templates:
                        h.flash_error(msg)
                        redirect(h.url_for(controller='package',
                                           action='new_resource', id=id))
                    else:
                        errors = {}
                        error_summary = {_('Error'): msg}
                        return self.new_resource_usmetadata(id, data, errors, error_summary)
                # we have a resource so let them add metadata
                # redirect(h.url_for(controller='package',
                #                    action='new_metadata', id=id))
                vars = self.get_package_info_usmetadata(id, context, errors, error_summary)
                package_type = self._get_package_type(id)
                self._setup_template_variables(context, {},package_type=package_type)
                return render('package/new_package_metadata.html', extra_vars=vars)

            data['package_id'] = id
            try:
                if resource_id:
                    data['id'] = resource_id
                    get_action('resource_update')(context, data)
                else:
                    get_action('resource_create')(context, data)
            except ValidationError, e:
                errors = e.error_dict
                error_summary = e.error_summary
                return self.new_resource_usmetadata(id, data, errors, error_summary)
            except NotAuthorized:
                abort(401, _('Unauthorized to create a resource'))
            except NotFound:
                abort(404,
                    _('The dataset {id} could not be found.').format(id=id))
            if save_action == 'go-metadata':
                # go to final stage of add dataset
                # redirect(h.url_for(controller='package',
                #                    action='new_metadata', id=id))
                #Github Issue # 129. Removing last stage of dataset creation.
                vars = self.get_package_info_usmetadata(id, context, errors, error_summary)
                package_type = self._get_package_type(id)
                self._setup_template_variables(context, {},package_type=package_type)
                return render('package/new_package_metadata.html', extra_vars=vars)
            elif save_action == 'go-dataset':
                # go to first stage of add dataset
                redirect(h.url_for(controller='package',
                                   action='edit', id=id))
            elif save_action == 'go-dataset-complete':
                # go to first stage of add dataset
                redirect(h.url_for(controller='package',
                                   action='read', id=id))
            else:
                # add more resources
                redirect(h.url_for(controller='package',
                                   action='new_resource', id=id))
        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary, 'action': 'new'}
        vars['pkg_name'] = id
        # get resources for sidebar
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}
        try:
            pkg_dict = get_action('package_show')(context, {'id': id})
        except NotFound:
            abort(404, _('The dataset {id} could not be found.').format(id=id))
        # required for nav menu
        vars['pkg_dict'] = pkg_dict
        template = 'package/new_resource_not_draft.html'
        if pkg_dict['state'] == 'draft':
            vars['stage'] = ['complete', 'active']
            template = 'package/new_resource.html'
        elif pkg_dict['state'] == 'draft-complete':
            vars['stage'] = ['complete', 'active', 'complete']
            template = 'package/new_resource.html'
        return render(template, extra_vars=vars)

class CommonCoreMetadataFormPlugin(p.SingletonPlugin, p.toolkit.DefaultDatasetForm):
    '''This plugin adds fields for the metadata (known as the Common Core) defined at
    https://github.com/project-open-data/project-open-data.github.io/blob/master/schema.md
    '''
    p.implements(p.ITemplateHelpers, inherit=False)
    p.implements(p.IConfigurer, inherit=False)
    p.implements(p.IDatasetForm, inherit=False)
    p.implements(p.interfaces.IRoutes, inherit=True)
    p.implements(p.interfaces.IPackageController, inherit=True)

    def edit(self, entity):
        #if dataset uses filestore to upload datafiles then make that dataset Public by default
        if hasattr(entity, 'type') and entity.type == u'dataset' and entity.private:
            for resource in entity.resources:
                if resource.url_type == u'upload':
                    entity.private = False
                    break
        return entity

    def before_map(self, m):
        m.connect('media_type','/dataset/new_resource/{id}',controller='ckanext.usmetadata.plugin:UsmetadataController',action='new_resource_usmetadata')
        return m

    def after_map(selfself, m):
        m.connect('media_type', '/api/2/util/resource/media_autocomplete',
                  controller='ckanext.usmetadata.plugin:MediaController', action='get_media_types')
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
        common_metadata = [x['id'] for x in required_metadata + required_if_applicable_metadata + expanded_metadata]

        try:
            new_dict['common_core']
        except KeyError:
            new_dict['common_core'] = {}

        reduced_extras = []
        new_dict['labels'] = dataset_labels
        try:
            for extra in new_dict['extras']:
                #to take care of legacy On values for data_quality
                if extra['key'] == 'data_quality' and extra['value'] == 'on':
                    extra['value'] = "true"
                elif extra['key'] == 'data_quality' and extra['value'] == 'False':
                    extra['value'] == "false"

                if extra['key'] in common_metadata:
                    new_dict['common_core'][extra['key']] = extra['value']
                else:
                    reduced_extras.append(extra)

            new_dict['extras'] = reduced_extras
        except KeyError as ex:
            log.debug('''Expected key ['%s'] not found, attempting to move common core keys to subdictionary''',
                      ex.message)
            #this can happen when a form fails validation, as all the data will now be as key,value pairs, not under extras,
            #so we'll move them to the expected point again to fill in the values
            # e.g.
            # { 'foo':'bar','publisher':'somename'} becomes {'foo':'bar', 'common_core':{'publisher':'somename'}}

            keys_to_remove = []

            #TODO remove debug
            log.debug('common core metadata: {0}'.format(common_metadata))
            for key, value in new_dict.iteritems():
                #TODO remove debug
                log.debug('checking key: {0}'.format(key))
                if key in common_metadata:
                    #TODO remove debug
                    log.debug('adding key: {0}'.format(key))
                    new_dict['common_core'][key] = value
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del new_dict[key]

        parent_dataset_options = db_utils.get_parent_organizations(20)
        parent_dataset_options[""] = ""
        new_dict['parent_dataset_options'] = parent_dataset_options
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

        #use convert_to_tags functions for taxonomy
        schema.update({
            'tag_string': [p.toolkit.get_validator('not_empty'),
                           p.toolkit.get_converter('convert_to_tags')],
            # 'resources': {
            #     'name': [p.toolkit.get_validator('not_empty')],
            #     'format': [p.toolkit.get_validator('not_empty')],
            # }
        })
        return schema

    def _modify_package_schema_update(self, schema):
        log.debug("_modify_package_schema_update called")
        for update in schema_updates_for_update:
            schema.update(update)

        #use convert_to_tags functions for taxonomy
        schema.update({
            'tag_string': [p.toolkit.get_validator('ignore_empty'),
                           p.toolkit.get_converter('convert_to_tags')],
            # 'resources': {
            #      'name': [p.toolkit.get_validator('not_empty'),
            #                p.toolkit.get_converter('convert_to_extras')],
            #      'format': [p.toolkit.get_validator('not_empty'),
            #                p.toolkit.get_converter('convert_to_extras')],
            # }
        })
        return schema

    def _modify_package_schema_show(self, schema):
        log.debug("_modify_package_schema_update_show called")
        for update in schema_updates_for_show:
            schema.update(update)

        return schema

    #See ckan.plugins.interfaces.IDatasetForm
    def create_package_schema(self):
        #action, api, package_create
        #action=new and controller=package
        schema = super(CommonCoreMetadataFormPlugin, self).create_package_schema()
        schema = self._create_package_schema(schema)
        return schema

    #See ckan.plugins.interfaces.IDatasetForm
    def update_package_schema(self):
        log.debug('update_package_schema')

        #find out action
        action = request.environ['pylons.routes_dict']['action']
        controller = request.environ['pylons.routes_dict']['controller']

        #new_resource and package
        #action, api, resource_create
        #action, api, package_update

        # if action == 'new_resource' and controller == 'package':
        #     schema = super(CommonCoreMetadataFormPlugin, self).update_package_schema()
        #     schema = self._create_resource_schema(schema)
        if action == 'edit' and controller == 'package':
            schema = super(CommonCoreMetadataFormPlugin, self).update_package_schema()
            schema = self._create_package_schema(schema)
        else:
            schema = super(CommonCoreMetadataFormPlugin, self).update_package_schema()
            schema = self._modify_package_schema_update(schema)

        return schema

    #See ckan.plugins.interfaces.IDatasetForm
    def show_package_schema(self):
        log.debug('show_package_schema called')
        schema = super(CommonCoreMetadataFormPlugin, self).show_package_schema()

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema['tags']['__extras'].append(p.toolkit.get_converter('free_tags_only'))

        #BELOW LINE MAY BE CAUSING SOLR INDEXING ISSUES.
        #schema = self._modify_package_schema_show(schema)

        return schema

    #Method below allows functions and other methods to be called from the Jinja template using the h variable
    # always_private hides Visibility selector, essentially meaning that all datasets are private to an organization
    def get_helpers(self):
        log.debug('get_helpers() called')
        return {'public_access_levels': access_levels,
                'required_metadata': required_metadata,
                'data_quality_options': data_quality_options,
                'is_parent_options': is_parent_options,
                'load_data_into_dict': self.load_data_into_dict,
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

        return json.dumps({'ResultSet': {'Result': retval}})
