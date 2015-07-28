'''Tests for the ckanext.example_iauthfunctions extension.

'''
import paste.fixture
import pylons.test

import ckan.model as model
import ckan.tests as tests
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class TestUsmetadataPlugin(object):
    '''Tests for the usmetadata.plugin module.

    '''

    @classmethod
    def setup_class(cls):
        '''Nose runs this method once to setup our test class.'''

        # Make the Paste TestApp that we'll use to simulate HTTP requests to
        # CKAN.
        cls.app = paste.fixture.TestApp(pylons.test.pylonsapp)

        # Test code should use CKAN's plugins.load() function to load plugins
        # to be tested.
        #plugins.load('usmetadata')

    def setup(self):
        '''Nose runs this method before each test method in our test class.'''

        # Access CKAN's model directly (bad) to create a sysadmin user and save
        # it against self for all test methods to access.
        self.sysadmin = model.User(name='test_sysadmin', sysadmin=True)
        model.Session.add(self.sysadmin)
        model.Session.commit()
        model.Session.remove()

    def teardown(self):
        '''Nose runs this method after each test method in our test class.'''

        # Rebuild CKAN's database after each test method, so that each test
        # method runs with a clean slate.
        model.repo.rebuild_db()

    @classmethod
    def teardown_class(cls):
        '''Nose runs this method once after all the test methods in our class
        have been run.

        '''
        # We have to unload the plugin we loaded, so it doesn't affect any
        # tests that run after ours.
        plugins.unload('usmetadata')

    #test is dataset is getting created successfully
    def test_package_creation(self):
        package_dict = tests.call_action_api(self.app, 'package_create', apikey=self.sysadmin.apikey,
                                             name='my_package',
                                             title='my package',
                                             notes='my package notes',
                                             tag_string='my_package',
                                             modified='2014-04-04',
                                             publisher='GSA',
                                             contact_name='john doe',
                                             contact_email='john.doe@gsa.com',
                                             unique_id='001',
                                             public_access_level='public',
                                             bureau_code='001:40',
                                             program_code='015:010',
                                             access_level_comment='Access level commemnt',
                                             parent_dataset = 'true'
                                             )
        assert package_dict['name'] == 'my_package'


    # test resource creation
    def test_resource_create(self):
        package_dict = tests.call_action_api(self.app, 'package_create', apikey=self.sysadmin.apikey,
                                             name='my_package',
                                             title='my package',
                                             notes='my package notes',
                                             tag_string='my_package',
                                             modified='2014-04-04',
                                             publisher='GSA',
                                             contact_name='john doe',
                                             contact_email='john.doe@gsa.com',
                                             unique_id='001',
                                             public_access_level='public',
                                             bureau_code='001:40',
                                             program_code='015:010',
                                             access_level_comment='Access level commemnt',
                                             resources=[
                                                 {
                                                    'name':'my_resource',
                                                    'url':'www.google.com',
                                                    'description':'description'},
                                                 { 'name':'my_resource_1',
                                                    'url':'www.google.com',
                                                    'description':'description_2'},
                                                ]
                                             )
        assert package_dict['name'] == 'my_package'
        assert package_dict['resources'][0]['name'] == 'my_resource'

        resource_dict = tests.call_action_api(self.app, 'resource_create', apikey=self.sysadmin.apikey,
                                              package_id = package_dict['id'],
                                              name='my_resource_2',
                                              url='www.google.com',
                                              description='description_3'
                                             )
        assert resource_dict['name'] == 'my_resource_2'

    #test package update
    def test_package_update(self):
        package_dict = tests.call_action_api(self.app, 'package_create', apikey=self.sysadmin.apikey,
                                             name='my_package',
                                             title='my package',
                                             notes='my package notes',
                                             tag_string='my_package',
                                             modified='2014-04-04',
                                             publisher='GSA',
                                             contact_name='john doe',
                                             contact_email='john.doe@gsa.com',
                                             unique_id='001',
                                             public_access_level='public',
                                             bureau_code='001:40',
                                             program_code='015:010',
                                             access_level_comment='Access level commemnt'
                                             )
        assert package_dict['name'] == 'my_package'
        package_dict_update = tests.call_action_api(self.app, 'package_update', apikey=self.sysadmin.apikey,
                                             name='my_package',
                                             title='my package update',
                                             notes='my package notes update',
                                             tag_string='my_package',
                                             modified='2014-04-05',
                                             publisher='GSA',
                                             contact_name='john doe jr',
                                             contact_email='john.doe1@gsa.com',
                                             unique_id='002',
                                             public_access_level='public',
                                             bureau_code='001:41',
                                             program_code='015:011',
                                             access_level_comment='Access level commemnt update'
                                             )
        assert package_dict_update['title'] == 'my package update'

        assert package_dict_update['extras'][0]['value'] == 'Access level commemnt update'
        assert package_dict_update['extras'][1]['value'] == '001:41'
        assert package_dict_update['extras'][2]['value'] == 'john.doe1@gsa.com'
        assert package_dict_update['extras'][3]['value'] == 'john doe jr'
        assert package_dict_update['extras'][4]['value'] == '2014-04-05'
        assert package_dict_update['extras'][5]['value'] == '015:011'
        assert package_dict_update['extras'][6]['value'] == 'public'
        assert package_dict_update['extras'][7]['value'] == 'GSA'
        assert package_dict_update['extras'][8]['value'] == '002'
