'''Tests for the ckanext.example_iauthfunctions extension.

'''
from builtins import object
import json
import pytest
import six
from ckanext.usmetadata import db_utils
from ckan.tests.helpers import FunctionalTestBase, reset_db
from ckan.tests import factories


@pytest.mark.usefixtures("with_request_context")
class TestUsmetadataPlugin(FunctionalTestBase):
    '''Tests for the usmetadata.plugin module.'''

    @classmethod
    def setup(cls):
        reset_db()

    @classmethod
    def setup_class(cls):
        super(TestUsmetadataPlugin, cls).setup_class()

    def create_datasets(self):
        self.sysadmin = factories.Sysadmin(name='admin')
        self.user = factories.User()
        self.organization = factories.Organization()
        if six.PY2:
            self.extra_environ = {'REMOTE_USER': self.sysadmin['name'].encode('ascii')}
            self.extra_environ_user = {'REMOTE_USER': self.user['name'].encode('ascii')}
        else:
            self.extra_environ = {'REMOTE_USER': self.sysadmin['name']}
            self.extra_environ_user = {'REMOTE_USER': self.user['name']}
        # token_dict = call_action('api_token_create')
        # print(token_dict)

        self.dataset1 = {
            'name': 'my_package_000',
            'title': 'my package',
            'notes': 'my package notes',
            'public_access_level': 'public',
            'access_level_comment': 'Access level comment',
            'unique_id': '000',
            'contact_name': 'Jhon',
            'program_code': '018:001',
            'bureau_code': '019:20',
            'contact_email': 'jhon@mail.com',
            'publisher': 'Publicher 01',
            'modified': '2019-01-27 11:41:21',
            'tag_string': 'mypackage,tag01,tag02',
            'parent_dataset': 'true',
            'owner_org': self.organization['id']
        }

        for key in self.sysadmin:
            if key not in ['id', 'name']:
                self.dataset1.update({key: self.sysadmin[key]})
        self.dataset1 = factories.Dataset(**self.dataset1)

        self.dataset2 = {
            'name': 'my_package_001',
            'title': 'my package 1',
            'notes': 'my package notes',
            'tag_string': 'my_package',
            'modified': '2014-04-04',
            'publisher': 'GSA',
            'publisher_1': 'OCSIT',
            'contact_name': 'john doe',
            'contact_email': 'john.doe@gsa.com',
            'unique_id': '001',
            'public_access_level': 'public',
            'bureau_code': '001:40',
            'program_code': '015:010',
            'access_level_comment': 'Access level commemnt',
            'license_id': 'http://creativecommons.org/publicdomain/zero/1.0/',
            'license_new': 'http://creativecommons.org/publicdomain/zero/1.0/',
            'spatial': 'Lincoln, Nebraska',
            'temporal': '2000-01-15T00:45:00Z/2010-01-15T00:06:00Z',
            'category': ["vegetables", "produce"],
            'data_dictionary': 'www.google.com',
            'data_dictionary_type': 'tex/csv',
            'data_quality': 'true',
            'publishing_status': 'open',
            'accrual_periodicity': 'annual',
            'conforms_to': 'www.google.com',
            'homepage_url': 'www.google.com',
            'language': 'us-EN',
            'primary_it_investment_uii': '021-123456789',
            'related_documents': 'www.google.com',
            'release_date': '2014-01-02',
            'system_of_records': 'www.google.com',
            'is_parent': 'true',
            'accessURL': 'www.google.com',
            'webService': 'www.gooogle.com',
            'format': 'text/csv',
            'formatReadable': 'text/csv',
            'resources': [
                {
                    'name': 'my_resource',
                    'url': 'www.google.com',
                    'description': 'description'},
                {
                    'name': 'my_resource_1',
                    'url': 'www.google.com',
                    'description': 'description_2'}],
            'owner_org': self.organization['id']
        }

    def test_package_creation(self):
        '''
        test if dataset is getting created successfully
        '''
        self.create_datasets()
        self.app = self._get_test_app()

        # This test relies on 'factories.dataset' creating the dataset and this 'get'
        # validates that the dataset was created properly
        package_dict = self.app.get('/api/3/action/package_show?id=my_package_000',
                                    extra_environ=self.extra_environ)

        result = json.loads(package_dict.body)['result']
        assert result['name'] == 'my_package_000'

    def test_resource_create(self):
        '''
        test resource creation
        '''
        self.create_datasets()
        self.app = self._get_test_app()

        # This test added the dataset through the 'package_create' route and then
        # checks that the dataset was created properly.
        package_dict = self.app.post('/api/3/action/package_create',
                                     headers={'Authorization': self.sysadmin.get('apikey').encode('ascii'),
                                              'Content-type': 'application/json'},
                                     params=json.dumps(self.dataset2),
                                     extra_environ=self.extra_environ)

        result = json.loads(package_dict.body)['result']
        assert result['name'] == 'my_package_001'
        assert result['resources'][0]['name'] == 'my_resource'
        assert result['resources'][1]['name'] == 'my_resource_1'

        dataset2b = {
            'package_id': result['id'],
            'name': 'my_resource_2b',
            'url': 'www.google.com',
            'description': 'description_3',
        }

        resource_dict = self.app.post('/api/3/action/resource_create',
                                      params=dataset2b,
                                      headers={'Authorization': self.sysadmin.get('apikey').encode('ascii'),
                                               'X-CKAN-API-Key': self.sysadmin.get('apikey').encode('ascii')},
                                      extra_environ=self.extra_environ)

        result = json.loads(resource_dict.body)['result']
        assert result['name'] == 'my_resource_2b'

    def test_package_update(self):
        '''
        test package update
        '''
        self.create_datasets()
        self.app = self._get_test_app()

        update_dict = {
            'name': 'my_package_000',
            'title': 'my package update',
            'notes': 'my package notes update',
            'tag_string': 'my_package',
            'modified': '2014-04-05',
            'publisher': 'GSA',
            'contact_name': 'john doe jr',
            'contact_email': 'john.doe1@gsa.com',
            'unique_id': '002',
            'public_access_level': 'public',
            'bureau_code': '001:41',
            'program_code': '015:011',
            'access_level_comment': 'Access level commemnt update'
        }

        package_dict_update = self.app.post('/api/3/action/package_update',
                                            params=update_dict,
                                            headers={'Authorization': self.sysadmin.get('apikey').encode('ascii'),
                                                     'X-CKAN-API-Key': self.sysadmin.get('apikey').encode('ascii')},
                                            extra_environ=self.extra_environ)

        result = json.loads(package_dict_update.body)['result']
        assert result['title'] == 'my package update'
        updates = {}
        for keyvalue in result['extras']:
            updates[keyvalue['key']] = keyvalue['value']
        assert updates['access_level_comment'] == 'Access level commemnt update'
        assert updates['bureau_code'] == '001:41'
        assert updates['contact_email'] == 'john.doe1@gsa.com'
        assert updates['contact_name'] == 'john doe jr'
        assert updates['modified'] == '2014-04-05'
        assert updates['program_code'] == '015:011'
        assert updates['public_access_level'] == 'public'
        assert updates['publisher'] == 'GSA'
        assert updates['unique_id'] == '002'

    def test_package_parent_dataset(self):
        '''
        test parent dataset
        '''
        self.create_datasets()
        self.app = self._get_test_app()

        title = db_utils.get_organization_title(self.dataset1['id'])
        assert title == 'my package'

        class Config(object):
            def __init__(self, **kwds):
                self.__dict__.update(kwds)

        class Userobj(object):
            def __init__(self, outer_instance=None, **kwds):
                self.outer_instance = outer_instance
                self.__dict__.update(kwds)

            def get_group_ids(self):
                return [self.outer_instance.organization['id']]

        config = Config(userobj=Userobj(outer_instance=self, sysadmin=True))
        items = db_utils.get_parent_organizations(config)
        assert self.organization['id'] not in items

        config = Config(userobj=Userobj(outer_instance=self, sysadmin=False))
        items = db_utils.get_parent_organizations(config)
        assert self.organization['id'] not in items

    # # TODO:Add assertions for all field validations
    # def test_validate_dataset_action(self):
    #     url = ('/api/2/util/resource/validate_dataset?pkg_name=&owner_org=' + self.org_dict['id'] + '&'
    #            'unique_id=000&rights=&license_url=&temporal=&described_by=&described_by_type=&conforms'
    #            '_to=&landing_page=&language=&investment_uii=&references=&issued=&system_of_records=')
    #     res = self.app.get(url)
    #     assert 'Success' in res

    # def test_validate_resource_action(self):
    #     res = self.app.get('/api/2/util/resource/validate_resource?url=badurl'
    #                        '&resource_type=file&format=&describedBy=&describedByType=&conformsTo=')
    #     assert 'Invalid' in res

    # def test_get_content_type_action(self):
    #     res = self.app.get('/api/2/util/resource/content_type?url=badulr')
    #     assert 'InvalidFormat' in res

    # def test_get_media_types_action(self):
    #     res = self.app.get('/api/2/util/resource/media_autocomplete')
    #     assert 'CSV' in res

    # def test_get_media_types_autocomplete_action(self):
    #     res = self.app.get('/api/2/util/resource/media_autocomplete?incomplete=Excel')
    #     assert 'XLS' in res

    # def test_license_url_autocomplete_action(self):
    #     res = self.app.get('/api/2/util/resource/license_url_autocomplete?incomplete=d')
    #     assert 'creativecommons' in res
