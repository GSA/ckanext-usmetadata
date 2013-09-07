import unittest
import ckanext.usmetadata.plugin as plugin
import ckan.lib.navl.dictization_functions as df

class MetadataPluginTest(unittest.TestCase):
    '''These tests should run fine using a standard testrunner with no database or server backend'''

    # original_get_action = None
    # original_plugin = None

    # def setup_func(self):
        # self.original_get_action = toolkit.get_action
        # self.original_plugin = self.plugin

    # def teardown_func(self):
        # toolkit.get_action = self.original_get_action
        # self.plugin = self.original_plugin

    @classmethod
    def check_dicts_match(cls, dict1, dict2):
        '''helper function to compare two dicts to ensure that they match'''
        assert set(dict1) - set(dict2) == set([])
        assert set(dict2) - set(dict1) == set([])

    def test_load_data_into_dict_moves_required_metadata(self):
        '''Verify that load_data_into_dict() moves all entries matching required metadata from value of extras key to
        be (key:value) pairs of the dict.'''
        original = {'aardvark':'foo', 'extras':[{'key':'foo', 'value': 'bar'}, {'key':'publisher','value':'usda'}] }
        expected = {'aardvark':'foo', 'common_core': {'publisher':'usda'}, 'extras':[{'key':'foo', 'value': 'bar'}]}
        actual = plugin.CommonCoreMetadataFormPlugin().get_helpers()['load_data_into_dict'](original)
        MetadataPluginTest.check_dicts_match(expected, actual)

    def test_load_data_into_dict_moves_single_valued_extras_entry(self):
        '''Verify that load_data_into_dict() moves all entries matching required metadata from value of extras key to
        be (key:value) pairs of the dict.'''
        original = {'hi':'there', 'extras':[{'key': 'publisher', 'value':'USGS'}]}
        expected = {'hi':'there', 'common_core': {'publisher':'USGS'}, 'extras':[]}
        actual = plugin.CommonCoreMetadataFormPlugin().get_helpers()['load_data_into_dict'](original)
        MetadataPluginTest.check_dicts_match(expected, actual)

    def test_load_data_into_dict_moves_required_if_applicable_metadata(self):
        '''Verify that load_data_into_dict() moves all entries matching required metadata from value of extras key to
        be (key:value) pairs of the dict.'''
        original = {'aardvark':'foo', 'extras':[{'key':'spatial','value':'wayoutthere'}, {'key':'foo', 'value': 'bar'}, {'key':'publisher','value':'usda'}] }
        expected = {'aardvark':'foo', 'common_core': {'publisher':'usda', 'spatial':'wayoutthere'}, 'extras':[{'key':'foo', 'value': 'bar'}]}
        actual = plugin.CommonCoreMetadataFormPlugin().get_helpers()['load_data_into_dict'](original)
        MetadataPluginTest.check_dicts_match(expected, actual)

    def test_load_data_into_dict_fails_gracefully(self):
        '''Verify that load_data_into_dict() doesn't generate an error if extras not found'''
        original = {'aardvark':'foo', '__extras':[{'key':'foo', 'value': 'bar'}, {'key':'publisher','value':'usda'}] }
        expected = {'aardvark':'foo', 'common_core':{}, '__extras':[{'key':'foo', 'value': 'bar'}, {'key':'publisher','value':'usda'}] }
        actual = plugin.CommonCoreMetadataFormPlugin().get_helpers()['load_data_into_dict'](original)
        MetadataPluginTest.check_dicts_match(expected, actual)

    def test_load_data_into_dict_large(self):
        original = {'aardvark':'foo', 'extras': [{u'value': u'daily', u'key': u'accrual_periodicity', '__extras': {u'package_id': u'154dc150-bba6-4201-b4ff-1a684121e27e', u'revision_id': u'0fe96ac4-bac5-4ee5-a7e6-224f58897575'}}, {u'value': u'asdfa', u'key': u'category', '__extras': {u'revision_id': u'0fe96ac4-bac5-4ee5-a7e6-224f58897575', u'package_id': u'154dc150-bba6-4201-b4ff-1a684121e27e'}}, {u'value': u'contactmyemailaddr', u'key': u'contact_email', '__extras': {u'package_id': u'154dc150-bba6-4201-b4ff-1a684121e27e', u'revision_id': u'43774ce1-7b28-45d3-95cb-b98bc3860f6f'}} ]}
        expected = {'aardvark':'foo', 'common_core':{u'accrual_periodicity':u'value', u'category':'asdfa', u'contact_email':'contactmyemailaddr'}, 'extras':[]}
        actual = plugin.CommonCoreMetadataFormPlugin().get_helpers()['load_data_into_dict'](original)
        MetadataPluginTest.check_dicts_match(expected, actual)

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


    def __getSchemaFromMetadataDict__(self, id_value):
        """Convenience function to extract the schema for a given field"""
        for scheme in plugin.required_metadata:
            if scheme['id'] == 'public_access_level':
                return {scheme['id']:scheme['validators']}
        return {}

    # @with_setup(setup_func, teardown_func)
    # def test_get_access_levels(self):
    #     '''Test of get_access_levels() function when no exception is raised'''
    #     toolkit.get_action = MagicMock(name='get_action')
    #     toolkit.get_action.return_value = MagicMock(); #Don't care what gets called with the action
    #
    #     #Invoke unit under test
    #     plugin.get_access_levels()
    #
    #     #Verify results
    #     toolkit.get_action.assert_called_with('tag_list')
    #     toolkit.get_action.return_value.assert_called_with(data_dict={'vocabulary_id': 'access_levels'})

    #TODO probably remove all of the below
    # @with_setup(setup_func, teardown_func)
    # def test_get_access_levels_exception(self):
    #     '''Test of get_access_levels() function, ensure create_access_levels called when access_levels vocabulary
    #     doesn't exist'''
    #     toolkit.get_action = MagicMock(name='get_action', side_effect=toolkit.ObjectNotFound("Whoops, couldn't find "
    #                                                                                          "the access_levels "
    #                                                                                          "vocabulary. Bet ya didn't"
    #                                                                                          " create it"))
    #     plugin.create_access_levels = MagicMock(name='create_access_levels')
    #     plugin.get_user_context = MagicMock(name='get_user_context', return_value={'user':'aardvark'})
    #
    #     #Invoke unit under test
    #     plugin.get_access_levels()
    #
    #     #Verify results
    #     toolkit.get_action.assert_called_once_with('tag_list')
    #     #Verify call to create the access_levels vocabulary
    #     plugin.create_access_levels.assert_called_once_with(plugin.get_user_context.return_value)

    # #TODO Test addition of tag vocabularies
    # def test_get_user_context(self):
    #     context = plugin.get_user_context();
    #     assert context != None
    #     print context

    #TODO test customization of the form
    #TODO test addition to templates