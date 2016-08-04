import cgi
import collections
import copy
import datetime
import re
from logging import getLogger

import formencode.validators as v
import requests
from pylons import config

import ckan.lib.base as base
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.lib.plugins
import ckan.logic as logic
import ckan.model as model
import ckan.plugins as p
import db_utils
from ckan.common import _, json, request, c, g, response
from ckan.lib.base import BaseController

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
lookup_package_plugin = ckan.lib.plugins.lookup_package_plugin

import ckan.lib.helpers as h

# from ckan.plugins import implements, SingletonPlugin, toolkit, IConfigurer,
# ITemplateHelpers, IDatasetForm, IPackageController
# from formencode.validators import validators

redirect = base.redirect
log = getLogger(__name__)

URL_REGEX = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https:// or ftp:// or ftps://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

IANA_MIME_REGEX = re.compile(r"^[-\w]+/[-\w]+(\.[-\w]+)*([+][-\w]+)?$")

TEMPORAL_REGEX_1 = re.compile(
    r'^([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-2])(-?[1-7])?'
    r'|(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24\:?00)([\.,]'
    r'\d+(?!:))?)?(\17[0-5]\d([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?(\/)([\+-]?\d{4}'
    r'(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-2])(-?[1-7])?|'
    r'(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24\:?00)([\.,]'
    r'\d+(?!:))?)?(\17[0-5]\d([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?$'
)

TEMPORAL_REGEX_2 = re.compile(
    r'^(R\d*\/)?([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\4([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-2])'
    r'(-?[1-7])?|(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24\:?00)'
    r'([\.,]\d+(?!:))?)?(\18[0-5]\d([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?(\/)'
    r'P(?:\d+(?:\.\d+)?Y)?(?:\d+(?:\.\d+)?M)?(?:\d+(?:\.\d+)?W)?(?:\d+(?:\.\d+)?D)?(?:T(?:\d+(?:\.\d+)?H)?'
    r'(?:\d+(?:\.\d+)?M)?(?:\d+(?:\.\d+)?S)?)?$'
)

TEMPORAL_REGEX_3 = re.compile(
    r'^(R\d*\/)?P(?:\d+(?:\.\d+)?Y)?(?:\d+(?:\.\d+)?M)?(?:\d+(?:\.\d+)?W)?(?:\d+(?:\.\d+)?D)?(?:T(?:\d+'
    r'(?:\.\d+)?H)?(?:\d+(?:\.\d+)?M)?(?:\d+(?:\.\d+)?S)?)?\/([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])'
    r'(\4([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-2])(-?[1-7])?|(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))'
    r'([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24\:?00)([\.,]\d+(?!:))?)?(\18[0-5]\d([\.,]\d+)?)?([zZ]|([\+-])'
    r'([01]\d|2[0-3]):?([0-5]\d)?)?)?)?$'
)

LANGUAGE_REGEX = re.compile(
    r'^(((([A-Za-z]{2,3}(-([A-Za-z]{3}(-[A-Za-z]{3}){0,2}))?)|[A-Za-z]{4}|[A-Za-z]{5,8})(-([A-Za-z]{4}))?'
    r'(-([A-Za-z]{2}|[0-9]{3}))?(-([A-Za-z0-9]{5,8}|[0-9][A-Za-z0-9]{3}))*(-([0-9A-WY-Za-wy-z](-[A-Za-z0-9]{2,8})+))*'
    r'(-(x(-[A-Za-z0-9]{1,8})+))?)|(x(-[A-Za-z0-9]{1,8})+)|'
    r'((en-GB-oed|i-ami|i-bnn|i-default|i-enochian|i-hak|i-klingon|i-lux|i-mingo'
    r'|i-navajo|i-pwn|i-tao|i-tay|i-tsu|sgn-BE-FR|sgn-BE-NL|sgn-CH-DE)|'
    r'(art-lojban|cel-gaulish|no-bok|no-nyn|zh-guoyu|zh-hakka|zh-min|zh-min-nan|zh-xiang)))$'
)

PRIMARY_IT_INVESTMENT_UII_REGEX = re.compile(r"^[0-9]{3}-[0-9]{9}$")

ISSUED_REGEX = re.compile(
    r'^([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-2])(-?[1-7])?'
    r'|(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24\:?00)([\.,]'
    r'\d+(?!:))?)?(\17[0-5]\d([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?$'
)

REDACTED_REGEX = re.compile(
    r'^(\[\[REDACTED).*?(\]\])$'
)

REDACTION_STROKE_REGEX = re.compile(
    r'(\[\[REDACTED-EX B[\d]\]\])'
)

# excluded title, description, tags and last update as they're part of the default ckan dataset metadata
required_metadata = (
    {'id': 'title', 'validators': [p.toolkit.get_validator('not_empty'), unicode]},
    {'id': 'notes', 'validators': [p.toolkit.get_validator('not_empty'), unicode]},
    # {'id': 'tag_string', 'validators': [v.NotEmpty]},
    {'id': 'public_access_level',
     'validators': [v.Regex(r'^(public)|(restricted public)|(non-public)$')]},
    {'id': 'publisher', 'validators': [p.toolkit.get_validator('not_empty'), unicode]},
    {'id': 'contact_name', 'validators': [p.toolkit.get_validator('not_empty'), unicode]},
    {'id': 'contact_email', 'validators': [p.toolkit.get_validator('not_empty'), unicode]},
    # TODO should this unique_id be validated against any other unique IDs for this agency?
    {'id': 'unique_id', 'validators': [p.toolkit.get_validator('not_empty'), unicode]},
    {'id': 'modified', 'validators': [p.toolkit.get_validator('not_empty'), unicode]},
    {'id': 'bureau_code', 'validators': [v.Regex(
        r'^\d{3}:\d{2}(\s*,\s*\d{3}:\d{2}\s*)*$'
    )]},
    {'id': 'program_code', 'validators': [v.Regex(
        r'^\d{3}:\d{3}(\s*,\s*\d{3}:\d{3}\s*)*$'
    )]}
)

# used to bypass validation on create
required_metadata_update = (
    {'id': 'public_access_level',
     'validators': [v.Regex(r'^(public)|(restricted public)|(non-public)$')]},
    {'id': 'publisher', 'validators': [v.String(max=300)]},
    {'id': 'contact_name', 'validators': [v.String(max=300)]},
    {'id': 'contact_email', 'validators': [v.String(max=200)]},
    # TODO should this unique_id be validated against any other unique IDs for this agency?
    {'id': 'unique_id', 'validators': [v.String(max=100)]},
    {'id': 'modified', 'validators': [v.String(max=100)]},
    {'id': 'bureau_code', 'validators': [v.Regex(
        r'^\d{3}:\d{2}(\s*,\s*\d{3}:\d{2}\s*)*$'
    )]},
    {'id': 'program_code', 'validators': [v.Regex(
        r'^\d{3}:\d{3}(\s*,\s*\d{3}:\d{3}\s*)*$'
    )]}
)

# some of these could be excluded (e.g. related_documents) which can be captured from other ckan default data
expanded_metadata = (
    # issued
    {'id': 'release_date', 'validators': [v.Regex(
        r'^([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-2])(-?[1-7])?'
        r'|(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24\:?00)([\.,]'
        r'\d+(?!:))?)?(\17[0-5]\d([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?|(\[\[REDACTED).*?(\]\])$'
    ), v.String(max=500)]},
    {'id': 'accrual_periodicity', 'validators': [v.Regex(
        r'^([Dd]ecennial)|([Qq]uadrennial)|([Aa]nnual)|([Bb]imonthly)|([Ss]emiweekly)|([Dd]aily)|([Bb]iweekly)'
        r'|([Ss]emiannual)|([Bb]iennial)|([Tt]riennial)|([Tt]hree times a week)|([Tt]hree times a month)'
        r'|(Continuously updated)|([Mm]onthly)|([Qq]uarterly)|([Ss]emimonthly)|([Tt]hree times a year)'
        r'|([Ww]eekly)|([Hh]ourly)|([Cc]ompletely irregular)|([Ii]rregular)|(\[\[REDACTED).*?(\]\])$')]},
    {'id': 'language', 'validators': [v.Regex(
        r'^(((([A-Za-z]{2,3}(-([A-Za-z]{3}(-[A-Za-z]{3}){0,2}))?)|[A-Za-z]{4}|[A-Za-z]{5,8})(-([A-Za-z]{4}))?'
        r'(-([A-Za-z]{2}|[0-9]{3}))?(-([A-Za-z0-9]{5,8}|[0-9][A-Za-z0-9]{3}))*(-([0-9A-WY-Za-wy-z]'
        r'(-[A-Za-z0-9]{2,8})+))*(-(x(-[A-Za-z0-9]{1,8})+))?)|(x(-[A-Za-z0-9]{1,8})+)|((en-GB-oed'
        r'|i-ami|i-bnn|i-default|i-enochian|i-hak|i-klingon|i-lux|i-mingo|i-navajo|i-pwn|i-tao|i-tay|i-tsu'
        r'|sgn-BE-FR|sgn-BE-NL|sgn-CH-DE)|(art-lojban|cel-gaulish|no-bok|no-nyn|zh-guoyu|zh-hakka|zh-min'
        r'|zh-min-nan|zh-xiang)))$'
    )]},
    {'id': 'data_quality', 'validators': [v.String(max=1000)]},
    {'id': 'publishing_status', 'validators': [v.String(max=1000)]},
    {'id': 'is_parent', 'validators': [v.String(max=1000)]},
    {'id': 'parent_dataset', 'validators': [v.String(max=1000)]},
    # theme
    {'id': 'category', 'validators': [v.String(max=1000)]},
    # describedBy
    {'id': 'related_documents', 'validators': [v.String(max=2100)]},
    {'id': 'conforms_to', 'validators': [v.String(max=2100)]},
    {'id': 'homepage_url', 'validators': [v.String(max=2100)]},
    {'id': 'system_of_records', 'validators': [v.String(max=2100)]},
    {'id': 'primary_it_investment_uii', 'validators': [v.Regex(
        r'^([0-9]{3}-[0-9]{9})|(\[\[REDACTED).*?(\]\])$'
    )]},
    {'id': 'publisher_1', 'validators': [v.String(max=300)]},
    {'id': 'publisher_2', 'validators': [v.String(max=300)]},
    {'id': 'publisher_3', 'validators': [v.String(max=300)]},
    {'id': 'publisher_4', 'validators': [v.String(max=300)]},
    {'id': 'publisher_5', 'validators': [v.String(max=300)]}
)

exempt_allowed = [
    'title',
    'notes',
    'tag_string',
    'modified',
    'bureau_code',
    'program_code',
    'contact_name',
    'contact_email',
    'data_quality',
    'license_new',
    'spatial',
    'temporal',
    'category',
    'data_dictionary',
    'data_dictionary_type',
    'accrual_periodicity',
    'conforms_to',
    'homepage_url',
    'language',
    'publisher',
    'primary_it_investment_uii',
    'related_documents',
    'release_date',
    'system_of_records'
]

for field in exempt_allowed:
    expanded_metadata += ({'id': 'redacted_' + field, 'validators': [v.String(max=300)]},)

# excluded download_url, endpoint, format and license as they may be discoverable
required_if_applicable_metadata = (
    {'id': 'data_dictionary', 'validators': [v.String(max=2100)]},
    {'id': 'data_dictionary_type', 'validators': [v.String(max=2100)]},
    {'id': 'spatial', 'validators': [v.String(max=500)]},
    {'id': 'temporal', 'validators': [v.Regex(
        r'^([\-\dTWRZP/YMWDHMS:\+]{3,}/[\-\dTWRZP/YMWDHMS:\+]{3,})|(\[\[REDACTED).*?(\]\])$'
    )]},
    {'id': 'access_level_comment', 'validators': [v.String(max=255)]},
    {'id': 'license_new', 'validators': [v.String(max=2100)]}
)

# used for by passing API validation
required_metadata_by_pass_validation = (
    {'id': 'title', 'validators': [p.toolkit.get_validator('not_empty'), unicode]},
    {'id': 'notes', 'validators': [p.toolkit.get_validator('not_empty'), unicode]},
    {'id': 'public_access_level', 'validators': [v.String(max=2100)]},
    {'id': 'publisher', 'validators': [v.String(max=300)]},
    {'id': 'contact_name', 'validators': [v.String(max=2100)]},
    {'id': 'contact_email', 'validators': [v.String(max=2100)]},
    # TODO should this unique_id be validated against any other unique IDs for this agency?
    {'id': 'unique_id', 'validators': [v.String(max=100)]},
    {'id': 'modified', 'validators': [v.String(max=100)]},
    {'id': 'bureau_code', 'validators': [v.String(max=2100)]},
    {'id': 'program_code', 'validators': [v.String(max=2100)]}
)

# used for by passing API validation
expanded_metadata_by_pass_validation = (
    # issued
    {'id': 'release_date', 'validators': [v.String(max=2100)]},
    {'id': 'accrual_periodicity', 'validators': [v.String(max=2100)]},
    {'id': 'language', 'validators': [v.String(max=2100)]},
    {'id': 'data_quality', 'validators': [v.String(max=1000)]},
    {'id': 'publishing_status', 'validators': [v.String(max=1000)]},
    {'id': 'is_parent', 'validators': [v.String(max=1000)]},
    {'id': 'parent_dataset', 'validators': [v.String(max=1000)]},
    # theme
    {'id': 'category', 'validators': [v.String(max=1000)]},
    # describedBy
    {'id': 'related_documents', 'validators': [v.String(max=2100)]},
    {'id': 'conforms_to', 'validators': [v.String(max=2100)]},
    {'id': 'homepage_url', 'validators': [v.String(max=2100)]},
    {'id': 'rss_feed', 'validators': [v.String(max=2100)]},
    {'id': 'system_of_records', 'validators': [v.String(max=2100)]},
    {'id': 'system_of_records_none_related_to_this_dataset', 'validators': [v.String(max=2100)]},
    {'id': 'primary_it_investment_uii', 'validators': [v.String(max=2100)]},
    {'id': 'webservice', 'validators': [v.String(max=300)]},
    {'id': 'publisher_1', 'validators': [v.String(max=300)]},
    {'id': 'publisher_2', 'validators': [v.String(max=300)]},
    {'id': 'publisher_3', 'validators': [v.String(max=300)]},
    {'id': 'publisher_4', 'validators': [v.String(max=300)]},
    {'id': 'publisher_5', 'validators': [v.String(max=300)]}
)

# used for by passing API validation
required_if_applicable_metadata_by_pass_validation = (
    {'id': 'data_dictionary', 'validators': [v.String(max=2100)]},
    {'id': 'data_dictionary_type', 'validators': [v.String(max=2100)]},
    {'id': 'endpoint', 'validators': [v.String(max=2100)]},
    {'id': 'spatial', 'validators': [v.String(max=500)]},
    {'id': 'temporal', 'validators': [v.String(max=500)]},
    {'id': 'access_level_comment', 'validators': [v.String(max=255)]},
    {'id': 'license_new', 'validators': [v.String(max=2100)]}
)

accrual_periodicity = [u"Decennial", u"Quadrennial", u"Annual", u"Bimonthly", u"Semiweekly", u"Daily", u"Biweekly",
                       u"Semiannual", u"Biennial", u"Triennial",
                       u"Three times a week", u"Three times a month", u"Continuously updated", u"Monthly", u"Quarterly",
                       u"Semimonthly", u"Three times a year", u"Weekly", u"Hourly", u"Irregular"]

access_levels = ['public', 'restricted public', 'non-public']

publishing_status_options = ['Published', 'Draft']

license_options = {'': '',
                   'https://www.usa.gov/publicdomain/label/1.0/': 'http://www.usa.gov/publicdomain/label/1.0/',
                   'http://creativecommons.org/publicdomain/zero/1.0/': 'http://creativecommons.org/publicdomain/zero/1.0/',
                   'http://opendatacommons.org/licenses/pddl/': 'http://opendatacommons.org/licenses/pddl/',
                   'http://opendatacommons.org/licenses/by/1-0/': 'http://opendatacommons.org/licenses/by/1-0/',
                   'http://opendatacommons.org/licenses/odbl/': 'http://opendatacommons.org/licenses/odbl/',
                   'https://creativecommons.org/licenses/by/4.0': 'https://creativecommons.org/licenses/by/4.0',
                   'https://creativecommons.org/licenses/by-sa/4.0': 'https://creativecommons.org/licenses/by-sa/4.0',
                   'http://www.gnu.org/licenses/fdl-1.3.en.html0': 'http://www.gnu.org/licenses/fdl-1.3.en.html'}

data_quality_options = {'': '', 'true': 'Yes', 'false': 'No'}
is_parent_options = {'true': 'Yes', 'false': 'No'}

# Dictionary of all media types
# media_types = json.loads(open(os.path.join(os.path.dirname(__file__), 'media_types.json'), 'r').read())

# list(set(x)) returns list with unique values
media_types_dict = h.resource_formats()
media_types = list(set([row[1] for row in h.resource_formats().values()]))


# all required_metadata should be required
def get_req_metadata_for_create():
    log.debug('get_req_metadata_for_create')
    new_req_meta = copy.copy(required_metadata)
    validator = p.toolkit.get_validator('not_empty')
    for meta in new_req_meta:
        meta['validators'].append(validator)
    return new_req_meta


# used to bypass validation on create
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


def get_req_metadata_for_api_create():
    new_req_meta = copy.copy(required_metadata_by_pass_validation)
    validator = p.toolkit.get_validator('ignore_missing')
    for meta in new_req_meta:
        meta['validators'].append(validator)
    return new_req_meta


for meta in required_if_applicable_metadata:
    meta['validators'].append(p.toolkit.get_validator('ignore_empty'))

for meta in expanded_metadata:
    meta['validators'].append(p.toolkit.get_validator('ignore_empty'))

for meta in required_if_applicable_metadata_by_pass_validation:
    meta['validators'].append(p.toolkit.get_validator('ignore_empty'))

for meta in expanded_metadata_by_pass_validation:
    meta['validators'].append(p.toolkit.get_validator('ignore_empty'))

schema_updates_for_create = [{meta['id']: meta['validators'] + [p.toolkit.get_converter('convert_to_extras')]} for meta
                             in (get_req_metadata_for_create() + required_if_applicable_metadata + expanded_metadata)]
schema_updates_for_update = [{meta['id']: meta['validators'] + [p.toolkit.get_converter('convert_to_extras')]} for meta
                             in (get_req_metadata_for_update() + required_if_applicable_metadata + expanded_metadata)]
schema_updates_for_show = [{meta['id']: meta['validators'] + [p.toolkit.get_converter('convert_from_extras')]} for meta
                           in
                           (get_req_metadata_for_show_update() + required_if_applicable_metadata + expanded_metadata)]
schema_api_for_create = [{meta['id']: meta['validators'] + [p.toolkit.get_converter('convert_to_extras')]} for meta
                         in (
                             get_req_metadata_for_api_create() + required_if_applicable_metadata_by_pass_validation + expanded_metadata_by_pass_validation)]


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
        return {'data': data, 'errors': errors, 'error_summary': error_summary, 'pkg_name': id}

    def map_old_keys(self, error_summary):
        replace = {
            'Format': 'Media Type'
        }
        for old_key, new_key in replace.items():
            if old_key in error_summary.keys():
                error_summary[new_key] = error_summary[old_key]
                del error_summary[old_key]
        return error_summary

    def _resource_form(self, package_type):
        # backwards compatibility with plugins not inheriting from
        # DefaultDatasetPlugin and not implmenting resource_form
        plugin = lookup_package_plugin(package_type)
        if hasattr(plugin, 'resource_form'):
            result = plugin.resource_form()
            if result is not None:
                return result
        return lookup_package_plugin().resource_form()

    def new_resource_usmetadata(self, id, data=None, errors=None, error_summary=None):
        ''' FIXME: This is a temporary action to allow styling of the
        forms. '''
        if request.method == 'POST' and not data:
            save_action = request.params.get('save')
            data = data or \
                   clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(
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
                if str.lower(config.get('ckan.package.resource_required', 'true')) == 'true' and not len(
                        data_dict['resources']):
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
                        return self.new_resource_usmetadata(id, data, errors,
                                                            error_summary)
                # we have a resource so let them add metadata
                # redirect(h.url_for(controller='package',
                # action='new_metadata', id=id))
                extra_vars = self.get_package_info_usmetadata(id, context, errors, error_summary)
                package_type = self._get_package_type(id)
                self._setup_template_variables(context, {}, package_type=package_type)
                return render('package/new_package_metadata.html', extra_vars=extra_vars)

            data['package_id'] = id
            try:
                if resource_id:
                    data['id'] = resource_id
                    get_action('resource_update')(context, data)
                else:
                    get_action('resource_create')(context, data)
            except ValidationError, e:
                errors = e.error_dict
                # error_summary = e.error_summary
                error_summary = self.map_old_keys(e.error_summary)
                # return self.new_resource(id, data, errors, error_summary)
                return self.new_resource_usmetadata(id, data, errors, error_summary)

            except NotAuthorized:
                abort(401, _('Unauthorized to create a resource'))
            except NotFound:
                abort(404, _('The dataset {id} could not be found.'
                             ).format(id=id))
            if save_action == 'go-metadata':
                # go to final stage of add dataset
                # redirect(h.url_for(controller='package',
                # action='new_metadata', id=id))
                # Github Issue # 129. Removing last stage of dataset creation.
                extra_vars = self.get_package_info_usmetadata(id, context, errors, error_summary)
                package_type = self._get_package_type(id)
                self._setup_template_variables(context, {}, package_type=package_type)
                return render('package/new_package_metadata.html', extra_vars=extra_vars)
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

        # get resources for sidebar
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}
        try:
            pkg_dict = get_action('package_show')(context, {'id': id})
        except NotFound:
            abort(404, _('The dataset {id} could not be found.').format(id=id))
        try:
            check_access(
                'resource_create', context, {"package_id": pkg_dict["id"]})
        except NotAuthorized:
            abort(401, _('Unauthorized to create a resource for this package'))

        package_type = pkg_dict['type'] or 'dataset'

        errors = errors or {}
        error_summary = error_summary or {}
        extra_vars = {'data': data, 'errors': errors, 'error_summary': error_summary, 'action': 'new',
                      'resource_form_snippet': self._resource_form(package_type), 'dataset_type': package_type,
                      'pkg_name': id}
        # get resources for sidebar
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}
        try:
            pkg_dict = get_action('package_show')(context, {'id': id})
        except NotFound:
            abort(404, _('The dataset {id} could not be found.').format(id=id))
        # required for nav menu
        extra_vars['pkg_dict'] = pkg_dict
        template = 'package/new_resource_not_draft.html'
        if pkg_dict['state'] == 'draft':
            extra_vars['stage'] = ['complete', 'active']
            template = 'package/new_resource.html'
        elif pkg_dict['state'] == 'draft-complete':
            extra_vars['stage'] = ['complete', 'active', 'complete']
            template = 'package/new_resource.html'
        return render(template, extra_vars=extra_vars)


class CommonCoreMetadataFormPlugin(p.SingletonPlugin, p.toolkit.DefaultDatasetForm):
    """
    This plugin adds fields for the metadata (known as the Common Core) defined at
    https://github.com/project-open-data/project-open-data.github.io/blob/master/schema.md
    """
    p.implements(p.ITemplateHelpers, inherit=False)
    p.implements(p.IConfigurer, inherit=False)
    p.implements(p.IDatasetForm, inherit=False)
    p.implements(p.IResourceController, inherit=True)
    p.implements(p.interfaces.IRoutes, inherit=True)
    p.implements(p.interfaces.IPackageController, inherit=True)
    p.implements(p.interfaces.IOrganizationController, inherit=True)
    p.implements(p.IFacets, inherit=True)

    def validate(self, context, data_dict, schema, action):
        """
        Disabling validation during cloning process

        :param context:
        :param data_dict:
        :param schema:
        :param action:
        :return:
        """
        if context.get('cloning', False) or 'skip_validation' in data_dict.get('title', ''):
            data_dict, errors = p.toolkit.navl_validate(data_dict, schema, context)
            return data_dict, None

        return None

    def read(self, entity):
        """
        IPackageController.read && IOrganizationController.read
        page must not be accessible by visitors
        """
        visitor_allowed_actions = [
            'resource_download',  # download resource file
            'resource_read',  # resource read page
            'resource_view'  # resource view (data explorer)
        ]

        if not c.user and c.action not in visitor_allowed_actions:
            abort(401, _('Not authorized to see this page'))

    def before_search(self, search_params):
        """
        IPackageController.search
        page must not be accessible by visitors
        """
        if not c.user:
            abort(401, _('Not authorized to see this page'))

        return search_params

    @classmethod
    def usmetadata_filter(cls, data=None, mask='~~'):
        for redact in re.findall(REDACTION_STROKE_REGEX, data):
            data = data.replace(redact, mask)
        data = data.replace('[[/REDACTED]]', mask)
        # render our custom snippet
        return data

    @classmethod
    def usmetadata_shorten(cls, plain=None, extract_length=180):
        if not extract_length or len(plain) < extract_length:
            return plain
        return unicode(h.truncate(plain, length=extract_length, indicator='...', whole_word=True))

    @classmethod
    def resource_redacted_icon(cls, package, resource, field):
        redacted_key = 'redacted_' + field
        if 'extras' in package:
            extras = dict([(x['key'], x['value']) for x in package['extras']])
            if 'public_access_level' not in extras:
                return ''
            if extras['public_access_level'] not in ['non-public', 'restricted public']:
                return ''
            if redacted_key not in resource or not resource[redacted_key]:
                return ''
            return '<img src="/redacted_icon.png" class="redacted-icon" />'
        return ''

    @classmethod
    def redacted_icon(cls, package, field):
        redacted_key = 'redacted_' + field
        if 'common_core' in package and 'public_access_level' in package['common_core']:
            core = package['common_core']
            pal = core['public_access_level']
            if pal not in ['non-public', 'restricted public']:
                return ''
            if redacted_key not in core or not core[redacted_key]:
                return ''
            return '<img src="/redacted_icon.png" class="redacted-icon" />'
        elif 'extras' in package:
            extras = dict([(x['key'], x['value']) for x in package['extras']])
            if 'public_access_level' not in extras:
                return ''
            if extras['public_access_level'] not in ['non-public', 'restricted public']:
                return ''
            if redacted_key not in extras or not extras[redacted_key]:
                return ''
            return '<img src="/redacted_icon.png" class="redacted-icon" />'
        return ''

    # Add access level facet on dataset page
    def dataset_facets(self, facets_dict, package_type):
        if package_type <> 'dataset':
            return facets_dict
        d = collections.OrderedDict()
        d['public_access_level'] = 'Access Level'
        for k, v in facets_dict.items():
            d[k] = v
        return d

    # Add access level facet on organization page
    def organization_facets(self, facets_dict, organization_type, package_type):
        if organization_type <> 'organization':
            return facets_dict
        d = collections.OrderedDict()
        d['public_access_level'] = 'Access Level'
        for k, v in facets_dict.items():
            d[k] = v
        return d

    def before_show(self, resource_dict):
        labels = collections.OrderedDict()
        labels["accessURL new"] = "Access URL"
        labels["conformsTo"] = "Conforms To"
        labels["describedBy"] = "Described By"
        labels["describedByType"] = "Described By Type"
        labels["format"] = "Media Type"
        labels["formatReadable"] = "Format"
        labels["created"] = "Created"

        resource_dict['labels'] = labels

        return resource_dict

    def edit(self, entity):
        # if dataset uses filestore to upload datafiles then make that dataset Public by default
        if hasattr(entity, 'type') and entity.type == u'dataset' and entity.private:
            for resource in entity.resources:
                if resource.url_type == u'upload':
                    entity.private = False
                    break
        return entity

    @staticmethod
    def before_map(m):
        m.connect('media_type', '/dataset/new_resource/{id}',
                  controller='ckanext.usmetadata.plugin:UsmetadataController', action='new_resource_usmetadata')

        m.connect('media_type', '/api/2/util/resource/license_url_autocomplete',
                  controller='ckanext.usmetadata.plugin:LicenseURLController', action='get_license_url')

        m.connect('clone_dataset', '/dataset/{id}/clone',
                  controller='ckanext.usmetadata.plugin:CloneController', action='clone_dataset_metadata')

        return m

    @staticmethod
    def after_map(m):
        m.connect('media_type', '/api/2/util/resource/media_autocomplete',
                  controller='ckanext.usmetadata.plugin:MediaController', action='get_media_types')

        m.connect('content_type', '/api/2/util/resource/content_type',
                  controller='ckanext.usmetadata.plugin:CurlController', action='get_content_type')

        m.connect('resource_validation', '/api/2/util/resource/validate_resource',
                  controller='ckanext.usmetadata.plugin:ResourceValidator', action='validate_resource')

        m.connect('dataset_validation', '/api/2/util/resource/validate_dataset',
                  controller='ckanext.usmetadata.plugin:DatasetValidator', action='validate_dataset')

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
        parent_dataset_id = ""

        # Used to display user-friendly labels on dataset page
        dataset_labels = (
            ('name', 'Name'),
            ('title', 'Title'),
            ('notes', 'Description'),
            ('tag_string', 'Keywords (Tags)'),
            ('tags', 'Keywords (Tags)'),
            ('modified', 'Modified (Last Update)'),
            ('publisher', 'Publisher'),
            ('publisher_1', 'Sub-agency'),
            ('publisher_2', 'Sub-agency'),
            ('publisher_3', 'Sub-agency'),
            ('publisher_4', 'Sub-agency'),
            ('publisher_5', 'Sub-agency'),
            ('contact_name', 'Contact Name'),
            ('contact_email', 'Contact Email'),
            ('unique_id', 'Identifier'),
            ('public_access_level', 'Public Access Level'),
            ('bureau_code', 'Bureau Code'),
            ('program_code', 'Program Code'),
            ('access_level_comment', 'Rights'),
            ('license_id', 'License'),
            ('license_new', 'License'),
            ('spatial', 'Spatial'),
            ('temporal', 'Temporal'),
            ('category', 'Theme (Category)'),
            ('data_dictionary', 'Data Dictionary'),
            ('data_dictionary_type', 'Data Dictionary Type'),
            ('data_quality', 'Meets the agency Information Quality Guidelines'),
            ('publishing_status', 'Publishing Status'),
            ('accrual_periodicity', 'Accrual Periodicity (Frequency)'),
            ('conforms_to', 'Conforms To (Data Standard) '),
            ('homepage_url', 'Homepage Url'),
            ('language', 'Language'),
            ('primary_it_investment_uii', 'Primary IT Investment UII'),
            ('related_documents', 'Related Documents'),
            ('release_date', 'Release Date'),
            ('system_of_records', 'System of Records'),
            ('webservice', 'Webservice'),
            ('is_parent', 'Is parent dataset'),
            ('parent_dataset', 'Parent dataset'),
            ('accessURL', 'Download URL'),
            # ('accessURL_new', 'Access URL'),
            ('webService', 'Endpoint'),
            ('format', 'Media type'),
            ('formatReadable', 'Format')
        )

        new_dict['labels'] = collections.OrderedDict(dataset_labels)
        try:
            for extra in new_dict['extras']:
                # to take care of legacy On values for data_quality
                if extra['key'] == 'data_quality' and extra['value'] == 'on':
                    extra['value'] = "true"
                elif extra['key'] == 'data_quality' and extra['value'] == 'False':
                    extra['value'] = "false"

                if extra['key'] in common_metadata:
                    new_dict['common_core'][extra['key']] = extra['value']
                else:
                    reduced_extras.append(extra)

                # Check if parent dataset is present and if yes get details
                if extra['key'] == 'parent_dataset':
                    parent_dataset_id = extra['value']

            new_dict['extras'] = reduced_extras
        except KeyError as ex:
            log.debug('''Expected key ['%s'] not found, attempting to move common core keys to subdictionary''',
                      ex.message)
            # this can happen when a form fails validation, as all the data will now be as key,
            # value pairs, not under extras, so we'll move them to the expected point again to fill in the values
            # e.g.
            # { 'foo':'bar', 'publisher':'somename'} becomes {'foo':'bar', 'common_core':{'publisher':'somename'}}

            keys_to_remove = []

            # TODO remove debug
            log.debug('common core metadata: {0}'.format(common_metadata))
            for key, value in new_dict.iteritems():
                # TODO remove debug
                log.debug('checking key: {0}'.format(key))
                if key in common_metadata:
                    # TODO remove debug
                    log.debug('adding key: {0}'.format(key))
                    new_dict['common_core'][key] = value
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del new_dict[key]

        # reorder keys
        new_dict['ordered_common_core'] = collections.OrderedDict()
        for key in new_dict['labels']:
            if key in new_dict['common_core']:
                new_dict['ordered_common_core'][key] = new_dict['common_core'][key]

        parent_dataset_options = db_utils.get_parent_organizations(c)

        # If parent dataset is set, Make sure dataset dropdown always has that value.
        if parent_dataset_id != "":
            parent_dataset_title = db_utils.get_organization_title(parent_dataset_id)

            if parent_dataset_id not in parent_dataset_options:
                parent_dataset_options[parent_dataset_id] = parent_dataset_title

        new_dict['parent_dataset_options'] = parent_dataset_options

        redacted = {}
        for exempt_field in exempt_allowed:
            redacted_key = 'redacted_' + exempt_field
            if redacted_key in new_dict['common_core']:
                redacted[redacted_key] = new_dict['common_core'][redacted_key]
        new_dict['redacted_json'] = json.dumps(redacted)

        return new_dict

        # See ckan.plugins.interfaces.IDatasetForm

    def is_fallback(self):
        # Return True so that we use the extension's dataset form instead of CKAN's default for
        # /dataset/new and /dataset/edit
        return True

    # See ckan.plugins.interfaces.IDatasetForm
    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        #
        # return ['dataset', 'package']
        return []

    # See ckan.plugins.interfaces.IDatasetForm
    def update_config(self, config):
        # Instruct CKAN to look in the ```templates``` directory for customized templates and snippets
        p.toolkit.add_template_directory(config, 'templates')

        # Register this plugin's fanstatic directory with CKAN.
        # Here, 'fanstatic' is the path to the fanstatic directory
        # (relative to this plugin.py file), and 'example_theme' is the name
        # that we'll use to refer to this fanstatic directory from CKAN
        # templates.
        p.toolkit.add_resource('fanstatic', 'dataset_url')

        # Add this plugin's public dir to CKAN's extra_public_paths, so
        # that CKAN will use this plugin's custom static files.
        p.toolkit.add_public_directory(config, 'public')

    def _default_extras_schema(self):
        schema = {
            'id': [p.toolkit.get_validator('ignore')],
            'key': [p.toolkit.get_validator('not_empty'), unicode],
            'value': [p.toolkit.get_validator('not_missing')],
            'state': [p.toolkit.get_validator('ignore')],
            'deleted': [p.toolkit.get_validator('ignore_missing')],
            'revision_timestamp': [p.toolkit.get_validator('ignore')],
            '__extras': [p.toolkit.get_validator('ignore')],
        }
        return schema

    # See ckan.plugins.interfaces.IDatasetForm
    def _create_package_schema(self, schema):
        log.debug("_create_package_schema called")
        if request.path_qs == u'/api/action/package_create':
            for update in schema_api_for_create:
                schema.update(update)
        else:
            for update in schema_updates_for_create:
                schema.update(update)

        # use convert_to_tags functions for taxonomy
        schema.update({
            'tag_string': [p.toolkit.get_validator('not_empty'),
                           p.toolkit.get_converter('convert_to_tags')],
            'extras': self._default_extras_schema()
            # 'resources': {
            # 'name': [p.toolkit.get_validator('not_empty')],
            # 'format': [p.toolkit.get_validator('not_empty')],
            # }
        })
        return schema

    def _modify_package_schema_update(self, schema):
        log.debug("_modify_package_schema_update called")
        for update in schema_updates_for_update:
            schema.update(update)

        # use convert_to_tags functions for taxonomy
        schema.update({
            'tag_string': [p.toolkit.get_validator('ignore_empty'),
                           p.toolkit.get_converter('convert_to_tags')],
            'extras': self._default_extras_schema()
        })
        return schema

    def _modify_package_schema_show(self, schema):
        log.debug("_modify_package_schema_update_show called")
        for update in schema_updates_for_show:
            schema.update(update)

        return schema

    # See ckan.plugins.interfaces.IDatasetForm
    def create_package_schema(self):
        # action, api, package_create
        # action=new and controller=package
        schema = super(CommonCoreMetadataFormPlugin, self).create_package_schema()
        schema = self._create_package_schema(schema)
        return schema

    # See ckan.plugins.interfaces.IDatasetForm
    def update_package_schema(self):
        log.debug('update_package_schema')

        # find out action
        action = request.environ['pylons.routes_dict']['action']
        controller = request.environ['pylons.routes_dict']['controller']

        # new_resource and package
        # action, api, resource_create
        # action, api, package_update

        # if action == 'new_resource' and controller == 'package':
        # schema = super(CommonCoreMetadataFormPlugin, self).update_package_schema()
        # schema = self._create_resource_schema(schema)
        schema = super(CommonCoreMetadataFormPlugin, self).update_package_schema()
        if action == 'edit' and controller == 'package':
            schema = self._create_package_schema(schema)
        else:
            schema = self._modify_package_schema_update(schema)

        return schema

    # See ckan.plugins.interfaces.IDatasetForm
    def show_package_schema(self):
        log.debug('show_package_schema called')
        schema = super(CommonCoreMetadataFormPlugin, self).show_package_schema()

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema['tags']['__extras'].append(p.toolkit.get_converter('free_tags_only'))

        # BELOW LINE MAY BE CAUSING SOLR INDEXING ISSUES.
        # schema = self._modify_package_schema_show(schema)

        return schema

    # Method below allows functions and other methods to be called from the Jinja template using the h variable
    # always_private hides Visibility selector, essentially meaning that all datasets are private to an organization
    def get_helpers(self):
        log.debug('get_helpers() called')
        return {
            'public_access_levels': access_levels,
            'required_metadata': required_metadata,
            'data_quality_options': data_quality_options,
            'license_options': license_options,
            'is_parent_options': is_parent_options,
            'load_data_into_dict': self.load_data_into_dict,
            'accrual_periodicity': accrual_periodicity,
            'publishing_status_options': publishing_status_options,
            'always_private': True,
            'usmetadata_filter': self.usmetadata_filter,
            'usmetadata_shorten': self.usmetadata_shorten,
            'redacted_icon': self.redacted_icon,
            'resource_redacted_icon': self.resource_redacted_icon
        }


# AJAX validator
class DatasetValidator(BaseController):
    """Controller to validate resource"""

    @staticmethod
    def check_if_unique(unique_id, owner_org, pkg_name):
        packages = DatasetValidator.get_packages(owner_org)
        for package in packages:
            for extra in package['extras']:
                if extra['key'] == 'unique_id' and extra['value'] == unique_id and pkg_name != package['id']:
                    return package['name']
        return False

    @staticmethod
    def get_packages(owner_org):
        # Build the data.json file.
        packages = DatasetValidator.get_all_group_packages(group_id=owner_org)
        # get packages for sub-agencies.
        sub_agency = model.Group.get(owner_org)
        if 'sub-agencies' in sub_agency.extras.col.target \
                and sub_agency.extras.col.target['sub-agencies'].state == 'active':
            sub_agencies = sub_agency.extras.col.target['sub-agencies'].value
            sub_agencies_list = sub_agencies.split(",")
            for sub in sub_agencies_list:
                sub_packages = DatasetValidator.get_all_group_packages(group_id=sub)
                for sub_package in sub_packages:
                    packages.append(sub_package)

        return packages

    @staticmethod
    def get_all_group_packages(group_id):
        """
        Gets all of the group packages, public or private, returning them as a list of CKAN's dictized packages.
        """
        result = []
        for pkg_rev in model.Group.get(group_id).packages(with_private=True, context={'user_is_admin': True}):
            result.append(model_dictize.package_dictize(pkg_rev, {'model': model}))

        return result

    def validate_dataset(self):
        try:
            pkg_name = request.params.get('pkg_name', False)
            owner_org = request.params.get('owner_org', False)
            unique_id = request.params.get('unique_id', False)
            rights = request.params.get('rights', False)
            license_url = request.params.get('license_url', False)
            temporal = request.params.get('temporal', False)
            described_by = request.params.get('described_by', False)
            described_by_type = request.params.get('described_by_type', False)
            conforms_to = request.params.get('conforms_to', False)
            landing_page = request.params.get('landing_page', False)
            language = request.params.get('language', False)
            investment_uii = request.params.get('investment_uii', False)
            references = request.params.get('references', False)
            issued = request.params.get('issued', False)
            system_of_records = request.params.get('system_of_records', False)

            errors = {}
            warnings = {}

            matching_package = self.check_if_unique(unique_id, owner_org, pkg_name)
            if unique_id and matching_package:
                errors['unique_id'] = 'Already being used by ' + request.application_url + '/dataset/' \
                                      + matching_package

            if rights and len(rights) > 255:
                errors['access-level-comment'] = 'The length of the string exceeds limit of 255 chars'

            self.check_url(license_url, errors, warnings, 'license-new', True, True)
            self.check_url(described_by, errors, warnings, 'data_dictionary', True, True)
            self.check_url(conforms_to, errors, warnings, 'conforms_to', True, True)
            self.check_url(landing_page, errors, warnings, 'homepage_url', True, True)
            self.check_url(system_of_records, errors, warnings, 'system_of_records')

            if described_by_type and not IANA_MIME_REGEX.match(described_by_type) \
                    and not REDACTED_REGEX.match(described_by_type):
                errors['data_dictionary_type'] = 'The value is not valid IANA MIME Media type'

            if temporal and not REDACTED_REGEX.match(temporal):
                if "/" not in temporal:
                    errors['temporal'] = 'Invalid Temporal Format. Missing slash'
                elif not TEMPORAL_REGEX_1.match(temporal) \
                        and not TEMPORAL_REGEX_2.match(temporal) \
                        and not TEMPORAL_REGEX_3.match(temporal):
                    errors['temporal'] = 'Invalid Temporal Format'

            if language:  # and not REDACTED_REGEX.match(language):
                language = language.split(',')
                for s in language:
                    s = s.strip()
                    if not LANGUAGE_REGEX.match(s):
                        errors['language'] = 'Invalid Language Format: ' + str(s)

            if investment_uii and not REDACTED_REGEX.match(investment_uii):
                if not PRIMARY_IT_INVESTMENT_UII_REGEX.match(investment_uii):
                    errors['primary-it-investment-uii'] = 'Invalid Format. Must be `023-000000001` format'

            if references and not REDACTED_REGEX.match(references):
                references = references.split(',')
                for s in references:
                    url = s.strip()
                    if not URL_REGEX.match(url) and not REDACTED_REGEX.match(url):
                        errors['related_documents'] = 'One of urls is invalid: ' + url

            if issued and not REDACTED_REGEX.match(issued):
                if not ISSUED_REGEX.match(issued):
                    errors['release_date'] = 'Invalid Format'

            if errors:
                return json.dumps({'ResultSet': {'Invalid': errors, 'Warnings': warnings}})
            return json.dumps({'ResultSet': {'Success': errors, 'Warnings': warnings}})
        except Exception as ex:
            log.error('validate_resource exception: %s ', ex)
            return json.dumps({'ResultSet': {'Error': 'Unknown error'}})

    @staticmethod
    def check_url(url, errors, warnings, error_key, skip_empty=True, allow_redacted=False):
        if skip_empty and not url:
            return
        url = url.strip()
        if allow_redacted and REDACTED_REGEX.match(url):
            return
        if not URL_REGEX.match(url):
            errors[error_key] = 'Invalid URL format'
        return
        # else:
        # try:
        # r = requests.head(url, verify=False)
        # if r.status_code > 399:
        # r = requests.get(url, verify=False)
        # if r.status_code > 399:
        # warnings[error_key] = 'URL returns status ' + str(r.status_code) + ' (' + str(r.reason) + ')'
        # except Exception as ex:
        # log.error('check_url exception: %s ', ex)
        #         warnings[error_key] = 'Could not check url'


# AJAX validator
class ResourceValidator(BaseController):
    """Controller to validate resource"""

    def validate_resource(self):
        try:
            url = request.params.get('url', False)
            resource_type = request.params.get('resource_type', False)
            described_by = request.params.get('describedBy', False)
            described_by_type = request.params.get('describedByType', False)
            conforms_to = request.params.get('conformsTo', False)
            media_type = request.params.get('format', False)

            errors = {}
            warnings = {}

            # if media_type and not REDACTED_REGEX.match(media_type) \
            #         and not IANA_MIME_REGEX.match(media_type):
            # if media_type and not IANA_MIME_REGEX.match(media_type):
            #     errors['format'] = 'The value is not valid IANA MIME Media type'
            # elif not media_type and resource_type in ['file', 'upload']:
            #     if url or resource_type == 'upload':
            #         errors['format'] = 'The value is required for this type of resource'

            lower_types = [mtype.lower() for mtype in media_types]
            if media_type and media_type.lower() not in lower_types:
                errors['format'] = 'The value is not valid format'
            elif not media_type and resource_type in ['file', 'upload']:
                if url or resource_type == 'upload':
                    errors['format'] = 'The value is required for this type of resource'

            self.check_url(described_by, errors, warnings, 'describedBy', True, True)
            self.check_url(conforms_to, errors, warnings, 'conformsTo', True, True)

            if described_by_type and not REDACTED_REGEX.match(described_by_type.strip()) \
                    and not IANA_MIME_REGEX.match(described_by_type.strip()):
                errors['describedByType'] = 'The value is not valid IANA MIME Media type'

            if errors:
                return json.dumps({'ResultSet': {'Invalid': errors, 'Warnings': warnings}})
            return json.dumps({'ResultSet': {'Success': errors, 'Warnings': warnings}})
        except Exception as ex:
            log.error('validate_resource exception: %s ', ex)
            return json.dumps({'ResultSet': {'Error': 'Unknown error'}})

    @staticmethod
    def check_url(url, errors, warnings, error_key, skip_empty=True, allow_redacted=False):
        if skip_empty and not url:
            return
        url = url.strip()
        if allow_redacted and REDACTED_REGEX.match(url):
            return
        if not URL_REGEX.match(url):
            errors[error_key] = 'Invalid URL format'
        else:
            try:
                r = requests.head(url, verify=False)
                if r.status_code > 399:
                    r = requests.get(url, verify=False)
                    if r.status_code > 399:
                        warnings[error_key] = 'URL returns status ' + str(r.status_code) + ' (' + str(r.reason) + ')'
            except Exception as ex:
                log.error('check_url exception: %s ', ex)
                warnings[error_key] = 'Could not check url'


class CloneController(BaseController):
    """Controller to clone dataset metadata"""

    def clone_dataset_metadata(self, id):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}
        pkg_dict = get_action('package_show')(context, {'id': id})

        # udpate name and title
        pkg_dict['title'] = "Clone of " + pkg_dict['title']

        # name can not be more than 100 characters
        pkg_dict['name'] = pkg_dict['name'][:85] + "-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        pkg_dict['state'] = 'draft'
        pkg_dict['tag_string'] = ['']
        # remove id from original dataset
        if 'id' in pkg_dict:
            del pkg_dict['id']

        # remove resource for now.
        if 'resources' in pkg_dict:
            del pkg_dict['resources']

        # extras have to on top level. otherwise validation fails
        temp = {}
        for extra in pkg_dict['extras']:
            temp[extra['key']] = extra['value']

        del pkg_dict['extras']
        pkg_dict['extras'] = []
        for key, value in temp.iteritems():
            if key != 'title':
                pkg_dict[key] = value

        # somehow package is getting added to context. If we dont remove it current dataset gets updated
        if 'package' in context:
            del context['package']

        # disabling validation
        context['cloning'] = True

        # create new package
        pkg_dict_new = get_action('package_create')(context, pkg_dict)

        # redirect to draft edit
        redirect(h.url_for(controller='package', action='edit', id=pkg_dict_new['name']))


class CurlController(BaseController):
    """Controller to obtain info by url"""

    def get_content_type(self):
        # set content type (charset required or pylons throws an error)
        try:
            url = request.params.get('url', '')

            if REDACTED_REGEX.match(url):
                return json.dumps({'ResultSet': {
                    'CType': False,
                    'Status': 'OK',
                    'Redacted': True,
                    'Reason': '[[REDACTED]]'
                }})

            if not URL_REGEX.match(url):
                return json.dumps({'ResultSet': {'Error': 'Invalid URL', 'InvalidFormat': 'True', 'Red': 'True'}})

            r = requests.head(url, verify=False)
            method = 'HEAD'
            if r.status_code > 399 or r.headers.get('content-type') is None:
                r = requests.get(url, verify=False)
                method = 'GET'
                if r.status_code > 399 or r.headers.get('content-type') is None:
                    # return json.dumps({'ResultSet': {'Error': 'Returned status: ' + str(r.status_code)}})
                    return json.dumps({'ResultSet': {
                        'CType': False,
                        'Status': r.status_code,
                        'Reason': r.reason,
                        'Method': method}})
            content_type = r.headers.get('content-type')
            content_type = content_type.split(';', 1)
            unified_format = h.unified_resource_format(content_type[0])
            return json.dumps({'ResultSet': {
                'CType': unified_format,
                'Status': r.status_code,
                'Reason': r.reason,
                'Method': method}})
        except Exception as ex:
            log.error('get_content_type exception: %s ', ex)
            return json.dumps({'ResultSet': {'Error': 'unknown error'}})
            # return json.dumps({'ResultSet': {'Error': type(e).__name__}})


class MediaController(BaseController):
    """Controller to return the acceptable media types as JSON, powering the front end"""

    def get_media_types(self):
        # set content type (charset required or pylons throws an error)
        q = request.params.get('incomplete', '').lower()

        response.content_type = 'application/json; charset=UTF-8'

        retval = []

        if q in media_types_dict:
            retval.append(media_types_dict[q][1])

        media_keys = media_types_dict.keys()
        for media_type in media_keys:
            if q in media_type.lower() and media_types_dict[media_type][1] not in retval:
                retval.append(media_types_dict[media_type][1])
            if len(retval) >= 50:
                break

        return json.dumps({'ResultSet': {'Result': retval}})


class LicenseURLController(BaseController):
    """Controller to return the acceptable media types as JSON, powering the front end"""

    def get_license_url(self):
        # set content type (charset required or pylons throws an error)
        q = request.params.get('incomplete', '')

        response.content_type = 'application/json; charset=UTF-8'

        retval = []

        for key in license_options:
            retval.append(key)

        return json.dumps({'ResultSet': {'Result': retval}})
