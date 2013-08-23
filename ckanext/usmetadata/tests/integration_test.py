import unittest
import ckanext.usmetadata.plugin as plugin

class MetadataPluginIntegrationTest(unittest.TestCase):
    '''These tests are made to run using nosetests with database and backend integration'''
    # original_get_action = None
    # original_plugin = None

    # def setup_func(self):
        # self.original_get_action = toolkit.get_action
        # self.original_plugin = self.plugin

    # def teardown_func(self):
        # toolkit.get_action = self.original_get_action
        # self.plugin = self.original_plugin

    def test_something(self):
        #TODO stub
        assert False == True