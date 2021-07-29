from __future__ import absolute_import
from builtins import str
import copy
from logging import getLogger

import formencode.validators as v
import ckan.lib.helpers as h
import ckan.plugins as p

log = getLogger(__name__)

# excluded title, description, tags and last update as they're part of the default ckan dataset metadata
required_metadata = (
    {'id': 'title', 'validators': [p.toolkit.get_validator('not_empty'), str]},
    {'id': 'notes', 'validators': [p.toolkit.get_validator('not_empty'), str]},
    # {'id': 'tag_string', 'validators': [v.NotEmpty]},
    {'id': 'public_access_level',
     'validators': [v.Regex(r'^(public)|(restricted public)|(non-public)$')]},
    {'id': 'publisher', 'validators': [p.toolkit.get_validator('not_empty'), str]},
    {'id': 'contact_name', 'validators': [p.toolkit.get_validator('not_empty'), str]},
    {'id': 'contact_email', 'validators': [p.toolkit.get_validator('not_empty'), str]},
    # TODO should this unique_id be validated against any other unique IDs for this agency?
    {'id': 'unique_id', 'validators': [p.toolkit.get_validator('not_empty'), str]},
    {'id': 'modified', 'validators': [p.toolkit.get_validator('not_empty'), str]},
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
        r'|R\/P(?:(\d+(?:[\.,]\d+)?)Y)?(?:(\d+(?:[\.,]\d+)?)M)?(?:(\d+(?:[\.,]\d+)?)D)?(?:T(?:(\d+(?:[\.,]\d+)?)H)?(?:(\d+(?:[\.,]\d+)?)M)?(?:(\d+(?:[\.,]\d+)?)S)?)?$'  # NOQA E501  # ISO 8601 duration
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
    {'id': 'title', 'validators': [p.toolkit.get_validator('not_empty'), str]},
    {'id': 'notes', 'validators': [p.toolkit.get_validator('not_empty'), str]},
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
media_types = list(set([row[1] for row in list(h.resource_formats().values())]))


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
                         in (get_req_metadata_for_api_create() +  # NOQA
                             required_if_applicable_metadata_by_pass_validation +  # NOQA
                             expanded_metadata_by_pass_validation)]
