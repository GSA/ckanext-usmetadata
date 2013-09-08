import unittest
import ckanext.usmetadata.plugin as plugin
import ckan.lib.navl.dictization_functions as df



# This is a stub block to allow me to run unit tests from my IDE without using 'nosetests --with-pylons=/path/to/file
# from pylons import config
# from pylons.i18n.translation import set_lang
# import os
#
# conf = config.current_conf()
# if not conf['pylons.paths']['root']:
#     conf['pylons.paths']['root'] = os.path.abspath('.')
# if not conf.get('pylons.package'):
#     conf['pylons.package'] = 'example' # same as domain above
# set_lang('es', pylons_config=conf)

class MetadataPluginTest(unittest.TestCase):
    '''These tests should run fine using a standard testrunner with no database or server backend'''

    def test_load_data_into_dict_moves_required_metadata(self):
        '''Verify that load_data_into_dict() moves all entries matching required metadata from value of extras key to
        be (key:value) pairs of the dict.'''
        original = {'aardvark':'foo', 'extras':[{'key':'foo', 'value': 'bar'}, {'key':'publisher','value':'usda'}] }
        expected = {'aardvark':'foo', 'common_core': {'publisher':'usda'}, 'extras':[{'key':'foo', 'value': 'bar'}]}
        actual = plugin.CommonCoreMetadataFormPlugin().get_helpers()['load_data_into_dict'](original)
        MetadataPluginTest.__check_dicts_match__(expected, actual)

    def test_load_data_into_dict_moves_single_valued_extras_entry(self):
        '''Verify that load_data_into_dict() moves all entries matching required metadata from value of extras key to
        be (key:value) pairs of the dict.'''
        original = {'hi':'there', 'extras':[{'key': 'publisher', 'value':'USGS'}]}
        expected = {'hi':'there', 'common_core': {'publisher':'USGS'}, 'extras':[]}
        actual = plugin.CommonCoreMetadataFormPlugin().get_helpers()['load_data_into_dict'](original)
        MetadataPluginTest.__check_dicts_match__(expected, actual)

    def test_load_data_into_dict_moves_required_if_applicable_metadata(self):
        '''Verify that load_data_into_dict() moves all entries matching required metadata from value of extras key to
        be (key:value) pairs of the dict.'''
        original = {'aardvark':'foo', 'extras':[{'key':'spatial','value':'wayoutthere'}, {'key':'foo', 'value': 'bar'}, {'key':'publisher','value':'usda'}] }
        expected = {'aardvark':'foo', 'common_core': {'publisher':'usda', 'spatial':'wayoutthere'}, 'extras':[{'key':'foo', 'value': 'bar'}]}
        actual = plugin.CommonCoreMetadataFormPlugin().get_helpers()['load_data_into_dict'](original)
        MetadataPluginTest.__check_dicts_match__(expected, actual)

    def test_load_data_into_dict_fails_gracefully(self):
        '''Verify that load_data_into_dict() doesn't generate an error if extras not found'''
        original = {'aardvark':'foo', '__extras':[{'key':'foo', 'value': 'bar'}, {'key':'publisher','value':'usda'}] }
        expected = {'aardvark':'foo', 'common_core':{}, '__extras':[{'key':'foo', 'value': 'bar'}, {'key':'publisher','value':'usda'}] }
        actual = plugin.CommonCoreMetadataFormPlugin().get_helpers()['load_data_into_dict'](original)
        MetadataPluginTest.__check_dicts_match__(expected, actual)

    def test_load_data_into_dict_large(self):
        original = {'aardvark':'foo', 'extras': [{u'value': u'daily', u'key': u'accrual_periodicity', '__extras': {u'package_id': u'154dc150-bba6-4201-b4ff-1a684121e27e', u'revision_id': u'0fe96ac4-bac5-4ee5-a7e6-224f58897575'}}, {u'value': u'asdfa', u'key': u'category', '__extras': {u'revision_id': u'0fe96ac4-bac5-4ee5-a7e6-224f58897575', u'package_id': u'154dc150-bba6-4201-b4ff-1a684121e27e'}}, {u'value': u'contactmyemailaddr', u'key': u'contact_email', '__extras': {u'package_id': u'154dc150-bba6-4201-b4ff-1a684121e27e', u'revision_id': u'43774ce1-7b28-45d3-95cb-b98bc3860f6f'}} ]}
        expected = {'aardvark':'foo', 'common_core':{u'accrual_periodicity':u'value', u'category':'asdfa', u'contact_email':'contactmyemailaddr'}, 'extras':[]}
        actual = plugin.CommonCoreMetadataFormPlugin().get_helpers()['load_data_into_dict'](original)
        MetadataPluginTest.__check_dicts_match__(expected, actual)

    ###### Field: public_access_level #####

    def test_field_validation_public_access_level_public(self):

        data = {'public_access_level':'public'
        }
        schema = self.__getSchemaFromMetadataDict__('public_access_level')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})

        data['public_access_level']='Public'
        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})

    def test_field_validation_public_access_level_restricted(self):

        data = {'public_access_level':'restricted'
        }
        schema = self.__getSchemaFromMetadataDict__('public_access_level')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})

        data['public_access_level']='Restricted'
        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})

    def test_field_validation_public_access_level_bad_value(self):

        data = {'public_access_level':'BadValue'
        }
        schema = self.__getSchemaFromMetadataDict__('public_access_level')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'public_access_level':[u'The input is not valid']})

    def test_field_validation_public_access_level_rejects_empty(self):

        data = {'public_access_level':''
        }
        schema = self.__getSchemaFromMetadataDict__('public_access_level')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'public_access_level':[u'Missing value']})

    def test_field_validation_public_access_level_rejects_missing(self):

        data = {}
        schema = self.__getSchemaFromMetadataDict__('public_access_level')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'public_access_level':[u'Missing value']})

    ###### Field: publisher #####

    def test_field_validation_publisher_basic(self):

        data = {'publisher':'an agency'
        }
        schema = self.__getSchemaFromMetadataDict__('publisher')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})

    def test_field_validation_publisher_name_too_long(self):

        data = {'publisher':'a'*101
        }
        schema = self.__getSchemaFromMetadataDict__('publisher')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'publisher':[u'Enter a value not more than 100 characters long']})

    def test_field_validation_publisher_rejects_missing(self):

        data = {}
        schema = self.__getSchemaFromMetadataDict__('publisher')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'publisher':[u'Missing value']})

    def test_field_validation_publisher_rejects_empty(self):

        data = {'publisher':''}
        schema = self.__getSchemaFromMetadataDict__('publisher')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'publisher':[u'Missing value']})

    ###### Field: contact_name #####

    def test_field_validation_contact_basic(self):

        data = {'contact_name':'jim'
        }
        schema = self.__getSchemaFromMetadataDict__('contact_name')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})

    def test_field_validation_contact_name_too_long(self):

        data = {'contact_name':'a'*101
        }
        schema = self.__getSchemaFromMetadataDict__('contact_name')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'contact_name':[u'Enter a value not more than 100 characters long']})

    def test_field_validation_contact_rejects_missing(self):

        data = {}
        schema = self.__getSchemaFromMetadataDict__('contact_name')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'contact_name':[u'Missing value']})

    def test_field_validation_contact_rejects_empty(self):

        data = {'contact_name':''}
        schema = self.__getSchemaFromMetadataDict__('contact_name')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'contact_name':[u'Missing value']})

    ###### Field: contact_email #####

    def test_field_validation_contact_email_basic(self):

        data = {'contact_email':'a@foo.me'
        }
        schema = self.__getSchemaFromMetadataDict__('contact_email')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})

    def test_field_validation_contact_email_too_long(self):

        data = {'contact_email':'a'*50+'@foo.com'
        }
        schema = self.__getSchemaFromMetadataDict__('contact_email')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'contact_email':[u'Enter a value not more than 50 characters long']})

    def test_field_validation_contact_email_rejects_missing(self):

        data = {}
        schema = self.__getSchemaFromMetadataDict__('contact_email')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'contact_email':[u'Missing value']})

    def test_field_validation_contact_email_rejects_empty(self):

        data = {'contact_email':''}
        schema = self.__getSchemaFromMetadataDict__('contact_email')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'contact_email':[u'Missing value']})

    ###### Field: unique_id #####
    #TODO need test unique_id entered is verified to be unique for an organization

    def test_field_validation_uid_basic(self):

        data = {'unique_id':'jim'
        }
        schema = self.__getSchemaFromMetadataDict__('unique_id')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})

    def test_field_validation_uid_too_long(self):

        data = {'unique_id':'a'*101
        }
        schema = self.__getSchemaFromMetadataDict__('unique_id')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'unique_id':[u'Enter a value not more than 100 characters long']})

    def test_field_validation_uid_rejects_missing(self):

        data = {}
        schema = self.__getSchemaFromMetadataDict__('unique_id')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'unique_id':[u'Missing value']})

    def test_field_validation_uid_rejects_empty(self):

        data = {'unique_id':''}
        schema = self.__getSchemaFromMetadataDict__('unique_id')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'unique_id':[u'Missing value']})

    ###### Field: data_dictionary #####

    def test_field_validation_data_dictionary_basic(self):

        data = {'data_dictionary':'http://www.foo.com/my_data'
        }
        schema = self.__getSchemaFromMetadataDict__('data_dictionary')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})

    def test_field_validation_data_dictionary_bad_url(self):

        data = {'data_dictionary':'wow this isnt a valid url'
        }
        schema = self.__getSchemaFromMetadataDict__('data_dictionary')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'data_dictionary':[u'That is not a valid URL']})

    def test_field_validation_data_dictionary_too_long(self):

        data = {'data_dictionary': 'http://www.foo.com/'+('a'*350)
        }
        schema = self.__getSchemaFromMetadataDict__('data_dictionary')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'data_dictionary':[u'Enter a value not more than 350 characters long']})

    def test_field_validation_data_dictionary_ignores_missing(self):

        data = {}
        schema = self.__getSchemaFromMetadataDict__('data_dictionary')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})

    def test_field_validation_data_dictionary_ignores_empty(self):

        data = {'data_dictionary':''}
        schema = self.__getSchemaFromMetadataDict__('data_dictionary')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})

    ###### Field: endpoint #####

    def test_field_validation_endpoint_basic(self):

        data = {'endpoint':'http://www.foo.com/my_data'
        }
        schema = self.__getSchemaFromMetadataDict__('endpoint')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})

    def test_field_validation_endpoint_bad_url1(self):

        data = {'endpoint':'wow this isnt a valid url'
        }
        schema = self.__getSchemaFromMetadataDict__('endpoint')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'endpoint':[u'That is not a valid URL']})

    def test_field_validation_endpoint_bad_url2(self):

        data = {'endpoint':'wowthisisntavalidurl'
        }
        schema = self.__getSchemaFromMetadataDict__('endpoint')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'endpoint':[u'You must provide a full domain name (like wowthisisntavalidurl.com)']})

    def test_field_validation_endpoint_too_long(self):

        data = {'endpoint': 'http://www.foo.com/'+('a'*350)
        }
        schema = self.__getSchemaFromMetadataDict__('endpoint')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {'endpoint':[u'Enter a value not more than 350 characters long']})

    def test_field_validation_endpoint_ignores_missing(self):

        data = {}
        schema = self.__getSchemaFromMetadataDict__('endpoint')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})

    def test_field_validation_endpoint_ignores_empty(self):

        data = {'endpoint':''}
        schema = self.__getSchemaFromMetadataDict__('endpoint')

        converted_data, errors = df.validate(data, schema)
        self.assertEqual(errors, {})

    ###### Utility methods #####
    @classmethod
    def __getSchemaFromMetadataDict__(cls, id_value):
        """Convenience function to extract the schema for a given field"""
        for scheme in plugin.required_metadata+plugin.required_if_applicable_metadata+plugin.expanded_metadata:
            if scheme['id'] == id_value:
                return {scheme['id']:scheme['validators']}
        return {}

    @classmethod
    def __check_dicts_match__(cls, dict1, dict2):
        '''helper function to compare two dicts to ensure that they match'''
        assert set(dict1) - set(dict2) == set([])
        assert set(dict2) - set(dict1) == set([])