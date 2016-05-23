'''Tests for the ckanext.example_iauthfunctions extension.

'''
from ckanext.usmetadata import db_utils
import paste.fixture
from paste.registry import StackedObjectProxy
import pylons.test
import ckan.tests.factories as factories

import ckan.model as model
import ckan.tests as tests
import ckan.plugins as plugins
from ckan.common import c

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

        model.repo.rebuild_db()

    def setup(self):
        '''Nose runs this method before each test method in our test class.'''

        self.sysadmin = factories.Sysadmin()

        self.org_dict = tests.call_action_api(self.app, 'organization_create', apikey=self.sysadmin.get('apikey'), name='my_org_000')

        self.package_dict = tests.call_action_api(self.app, 'package_create', apikey=self.sysadmin.get('apikey'),
                                             name='my_package_000',
                                             title='my package',
                                             notes='my package notes',
                                             tag_string='my_package',
                                             modified='2014-04-04',
                                             publisher='GSA',
                                             contact_name='john doe',
                                             contact_email='john.doe@gsa.com',
                                             unique_id='000',
                                             public_access_level='public',
                                             bureau_code='001:40',
                                             program_code='015:010',
                                             access_level_comment='Access level commemnt',
                                             parent_dataset = 'true',
                                             ower_org = self.org_dict['id']
                                             )

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
        package_dict = tests.call_action_api(self.app, 'package_create', apikey=self.sysadmin.get('apikey'),
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
        package_dict = tests.call_action_api(self.app, 'package_create', apikey=self.sysadmin.get('apikey'),
                                             name='my_package',
                                             title='my package',
                                             notes='my package notes',
                                             tag_string='my_package',
                                             modified='2014-04-04',
                                             publisher='GSA',
                                             publisher_1='OCSIT',
                                             contact_name='john doe',
                                             contact_email='john.doe@gsa.com',
                                             unique_id='001',
                                             public_access_level='public',
                                             bureau_code='001:40',
                                             program_code='015:010',
                                             access_level_comment='Access level commemnt',
                                             license_id='http://creativecommons.org/publicdomain/zero/1.0/',
                                             license_new='http://creativecommons.org/publicdomain/zero/1.0/',
                                             spatial='Lincoln, Nebraska',
                                             temporal='2000-01-15T00:45:00Z/2010-01-15T00:06:00Z',
                                             category=["vegetables","produce"],
                                             data_dictionary='www.google.com',
                                             data_dictionary_type='tex/csv',
                                             data_quality='true',
                                             publishing_status='open',
                                             accrual_periodicity='annual',
                                             conforms_to='www.google.com',
                                             homepage_url='www.google.com',
                                             language='us-EN',
                                             primary_it_investment_uii='021-123456789',
                                             related_documents='www.google.com',
                                             release_date='2014-01-02',
                                             system_of_records='www.google.com',
                                             is_parent='true',
                                             accessURL='www.google.com',
                                             webService='www.gooogle.com',
                                             format='text/csv',
                                             formatReadable='text/csv',
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

        resource_dict = tests.call_action_api(self.app, 'resource_create', apikey=self.sysadmin.get('apikey'),
                                              package_id = package_dict['id'],
                                              name='my_resource_2',
                                              url='www.google.com',
                                              description='description_3'
                                             )
        assert resource_dict['name'] == 'my_resource_2'

    #test package update
    def test_package_update(self):
        package_dict = tests.call_action_api(self.app, 'package_create', apikey=self.sysadmin.get('apikey'),
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
        package_dict_update = tests.call_action_api(self.app, 'package_update', apikey=self.sysadmin.get('apikey'),
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

    #test parent dataset
    def test_package_parent_dataset(self):
        org_dict = tests.call_action_api(self.app, 'organization_create', apikey=self.sysadmin.get('apikey'),
                                             name='my_org')

        package_dict = tests.call_action_api(self.app, 'package_create', apikey=self.sysadmin.get('apikey'),
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
                                             parent_dataset = 'true',
                                             ower_org = org_dict['id']
                                             )
        assert package_dict['name'] == 'my_package'

        title = db_utils.get_organization_title(package_dict['id'])
        assert title == 'my package'

        class Config:
            def __init__(self, **kwds):
                self.__dict__.update(kwds)

        class Userobj:
            def __init__(self, **kwds):
                self.__dict__.update(kwds)

            def get_group_ids(self):
                return [org_dict['id']]

        config = Config(userobj=Userobj(sysadmin=True))
        items = db_utils.get_parent_organizations(config)
        assert org_dict['id'] not in items

        config = Config(userobj=Userobj(sysadmin=False))
        items = db_utils.get_parent_organizations(config)
        assert org_dict['id'] not in items

    #TODO:Add assertions for all field validations
    def test_validate_dataset_action(self):
        url = '/api/2/util/resource/validate_dataset?pkg_name=&owner_org='+ self.org_dict['id'] +'&unique_id=000&rights=&license_url=&temporal=&described_by=&described_by_type=&conforms_to=&landing_page=&language=&investment_uii=&references=&issued=&system_of_records='
        res = self.app.get(url)
        assert 'Success' in res

    def test_validate_resource_action(self):
        res = self.app.get('/api/2/util/resource/validate_resource?url=badurl&resource_type=file&format=&describedBy=&describedByType=&conformsTo=')
        assert 'Invalid' in res

    def test_get_content_type_action(self):
        res = self.app.get('/api/2/util/resource/content_type?url=badulr')
        assert 'InvalidFormat' in res

    def test_get_media_types_action(self):
        res = self.app.get('/api/2/util/resource/media_autocomplete')
        assert 'CSV' in res

    def test_get_media_types_autocomplete_action(self):
        res = self.app.get('/api/2/util/resource/media_autocomplete?incomplete=Excel')
        assert 'XLS' in res

    def test_license_url_autocomplete_action(self):
        res = self.app.get('/api/2/util/resource/license_url_autocomplete?incomplete=d')
        assert 'creativecommons' in res
