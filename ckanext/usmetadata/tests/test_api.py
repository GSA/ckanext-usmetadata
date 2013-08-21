import unittest
from ckanext.usmetadata.plugin import USMetadataPlugin


class MetadataPluginTest(unittest.TestCase):

    meta = USMetadataPlugin()

    def test_foo(self):
        assert True == True

    def test_fail(self):
        assert False == True

    def test_setup(self):
        assert self.meta == None

    #TODO Test addition of tag vocabularies via Action API
    #TODO test customization of the form
    #TODO test addition to templates