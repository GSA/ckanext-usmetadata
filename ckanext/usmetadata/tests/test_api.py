import unittest
from mock import MagicMock, patch
from nose.tools.nontrivial import with_setup
import ckanext.usmetadata.plugin as plugin
from ckan.plugins import toolkit

class MetadataPluginTest(unittest.TestCase):
    original_get_action = None
    original_plugin = None

    def test_get_access_levels(self):
        assert plugin.get_access_levels() != None

    # def setup_func(self):
    #     self.original_get_action = toolkit.get_action
    #     self.original_plugin = self.plugin
    #
    # def teardown_func(self):
    #     toolkit.get_action = self.original_get_action
    #     self.plugin = self.original_plugin
    #
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