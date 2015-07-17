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
        plugins.load('usmetadata')

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

    def _make_curators_group(self):
        '''This is a helper method for test methods to call when they want
        the 'curators' group to be created.

        '''
        # Create a user who will *not* be a member of the curators group.
        noncurator = tests.call_action_api(self.app, 'user_create',
                                           apikey=self.sysadmin.apikey,
                                           name='noncurator',
                                           email='email',
                                           password='password')

        # Create a user who will be a member of the curators group.
        curator = tests.call_action_api(self.app, 'user_create',
                                        apikey=self.sysadmin.apikey,
                                        name='curator',
                                        email='email',
                                        password='password')

        # Create the curators group, with the 'curator' user as a member.
        users = [{'name': curator['name'], 'capacity': 'member'}]
        curators_group = tests.call_action_api(self.app, 'group_create',
                                               apikey=self.sysadmin.apikey,
                                               name='curators',
                                               users=users)

        return (noncurator, curator, curators_group)

    #test is dataset is getting created successfully
    def test_package_creation(self):
        package_dict = tests.call_action_api(self.app, 'package_create', apikey=self.sysadmin.apikey,
                                             name='my_package',
                                             title='my package',
                                             notes='my package notes',
                                             tag_string='my_package',
                                             )
        assert package_dict['name'] == 'my_package'
