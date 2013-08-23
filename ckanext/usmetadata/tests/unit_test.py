import unittest
import ckanext.usmetadata.plugin as plugin

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
        expected = {'aardvark':'foo', 'publisher':'usda', 'extras':[{'key':'foo', 'value': 'bar'}]}
        actual = plugin.CommonCoreMetadataForm().get_helpers()['load_data_into_dict'](original)
        MetadataPluginTest.check_dicts_match(expected, actual)

    def test_load_data_into_dict_moves_single_valued_extras_entry(self):
        '''Verify that load_data_into_dict() moves all entries matching required metadata from value of extras key to
        be (key:value) pairs of the dict.'''
        original = {'hi':'there', 'extras':[{'key': 'publisher', 'value':'USGS'}]}
        expected = {'hi':'there', 'publisher':'USGS', 'extras':[]}
        actual = plugin.CommonCoreMetadataForm().get_helpers()['load_data_into_dict'](original)
        MetadataPluginTest.check_dicts_match(expected, actual)

    def test_load_data_into_dict_moves_required_if_applicable_metadata(self):
        '''Verify that load_data_into_dict() moves all entries matching required metadata from value of extras key to
        be (key:value) pairs of the dict.'''
        original = {'aardvark':'foo', 'extras':[{'key':'spatial','value':'wayoutthere'}, {'key':'foo', 'value': 'bar'}, {'key':'publisher','value':'usda'}] }
        expected = {'aardvark':'foo', 'publisher':'usda', 'spatial':'wayoutthere', 'extras':[{'key':'foo', 'value': 'bar'}]}
        actual = plugin.CommonCoreMetadataForm().get_helpers()['load_data_into_dict'](original)
        MetadataPluginTest.check_dicts_match(expected, actual)

    def test_load_data_into_dict_fails_gracefully(self):
        '''Verify that load_data_into_dict() doesn't generate an error if extras not found'''
        original = {'aardvark':'foo', '__extras':[{'key':'foo', 'value': 'bar'}, {'key':'publisher','value':'usda'}] }
        expected = original
        actual = plugin.CommonCoreMetadataForm().get_helpers()['load_data_into_dict'](original)
        MetadataPluginTest.check_dicts_match(expected, actual)

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