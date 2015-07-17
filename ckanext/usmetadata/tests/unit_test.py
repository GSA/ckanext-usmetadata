# import unittest
# import ckanext.usmetadata.plugin as plugin
# import ckan.lib.navl.dictization_functions as df
#
#
# import logging
#
# log = logging.getLogger(__name__)
#
# # This is a stub block to allow me to run unit tests from my IDE without using 'nosetests --with-pylons=/path/to/file
# # from pylons import config
# # from pylons.i18n.translation import set_lang
# # import os
# #
# # conf = config.current_conf()
# # if not conf['pylons.paths']['root']:
# #     conf['pylons.paths']['root'] = os.path.abspath('.')
# # if not conf.get('pylons.package'):
# #     conf['pylons.package'] = 'example' # same as domain above
# # set_lang('es', pylons_config=conf)
#
# class MetadataPluginTest(unittest.TestCase):
#     """These tests should run fine using a standard testrunner with no database or server backend"""
#
#     def testLoadDataIntoDictMovesRequiredMetadata(self):
#         """Verify that load_data_into_dict() moves all entries matching required metadata from value of extras key to
#         be (key:value) pairs of the dict."""
#         original = {'aardvark':'foo', 'extras':[{'key':'foo', 'value': 'bar'}, {'key':'publisher','value':'usda'}] }
#         expected = {'aardvark':'foo', 'common_core': {'publisher':'usda'}, 'extras':[{'key':'foo', 'value': 'bar'}]}
#         actual = plugin.CommonCoreMetadataFormPlugin().get_helpers()['load_data_into_dict'](original)
#         MetadataPluginTest.__check_dicts_match__(expected, actual)
#
#     def testLoadDataIntoDictMovesSingleValuedExtrasEntry(self):
#         """Verify that load_data_into_dict() moves all entries matching required metadata from value of extras key to
#         be (key:value) pairs of the dict."""
#         original = {'hi':'there', 'extras':[{'key': 'publisher', 'value':'USGS'}]}
#         expected = {'hi':'there', 'common_core': {'publisher':'USGS'}, 'extras':[]}
#         actual = plugin.CommonCoreMetadataFormPlugin().get_helpers()['load_data_into_dict'](original)
#         MetadataPluginTest.__check_dicts_match__(expected, actual)
#
#     def testLoadDataIntoDictMovesRequiredIfApplicableMetadata(self):
#         """Verify that load_data_into_dict() moves all entries matching required metadata from value of extras key to
#         be (key:value) pairs of the dict."""
#         original = {'aardvark':'foo', 'extras':[{'key':'spatial','value':'wayoutthere'}, {'key':'foo', 'value': 'bar'}, {'key':'publisher','value':'usda'}] }
#         expected = {'aardvark':'foo', 'common_core': {'publisher':'usda', 'spatial':'wayoutthere'}, 'extras':[{'key':'foo', 'value': 'bar'}]}
#         actual = plugin.CommonCoreMetadataFormPlugin().get_helpers()['load_data_into_dict'](original)
#         MetadataPluginTest.__check_dicts_match__(expected, actual)
#
#     def testLoadDataIntoDictFailsGracefully(self):
#         """Verify that load_data_into_dict() doesn't generate an error if extras not found"""
#         original = {'aardvark':'foo', '__extras':[{'key':'foo', 'value': 'bar'}, {'key':'publisher','value':'usda'}] }
#         expected = {'aardvark':'foo', 'common_core':{}, '__extras':[{'key':'foo', 'value': 'bar'}, {'key':'publisher','value':'usda'}] }
#         actual = plugin.CommonCoreMetadataFormPlugin().get_helpers()['load_data_into_dict'](original)
#         MetadataPluginTest.__check_dicts_match__(expected, actual)
#
#     def testLoadDataIntoDictLarge(self):
#         original = {'aardvark':'foo', 'extras': [{u'value': u'daily', u'key': u'accrual_periodicity', '__extras': {u'package_id': u'154dc150-bba6-4201-b4ff-1a684121e27e', u'revision_id': u'0fe96ac4-bac5-4ee5-a7e6-224f58897575'}}, {u'value': u'asdfa', u'key': u'category', '__extras': {u'revision_id': u'0fe96ac4-bac5-4ee5-a7e6-224f58897575', u'package_id': u'154dc150-bba6-4201-b4ff-1a684121e27e'}}, {u'value': u'contactmyemailaddr', u'key': u'contact_email', '__extras': {u'package_id': u'154dc150-bba6-4201-b4ff-1a684121e27e', u'revision_id': u'43774ce1-7b28-45d3-95cb-b98bc3860f6f'}} ]}
#         expected = {'aardvark':'foo', 'common_core':{u'accrual_periodicity':u'value', u'category':'asdfa', u'contact_email':'contactmyemailaddr'}, 'extras':[]}
#         actual = plugin.CommonCoreMetadataFormPlugin().get_helpers()['load_data_into_dict'](original)
#         MetadataPluginTest.__check_dicts_match__(expected, actual)
#
#     def testLoadDataIntoDictNoExtra(self):
#         """Verify that when no '__extras' key exist, load_data_into_dict() will move any common core metadata in key value pairs into a dict under
#         the key 'common_core'"""
#         original = { 'foo':'bar','publisher':'somename', 'foo2':'bar2', 'data_dictionary':'something', 'system_of_records':'somesystem'}
#         expected = {'foo':'bar', 'common_core':{'data_dictionary':'something', 'publisher':'somename', 'system_of_records':'somesystem'}, 'foo2':'bar2'}
#         actual = plugin.CommonCoreMetadataFormPlugin().get_helpers()['load_data_into_dict'](original)
#
#         log.debug('actual: {0}'.format(actual))
#         MetadataPluginTest.__check_dicts_match__(expected, actu   al)
#
#
#     ###### Field: public_access_level #####
#
#     def testFieldValidationPublicAccessLevelPublic(self):
#
#         data = {'public_access_level':'public'
#         }
#         schema = self.__getSchemaFromMetadataDict__('public_access_level')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#         data['public_access_level']='Public'
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationPublicAccessLevelRestricted(self):
#
#         data = {'public_access_level':'restricted public'
#         }
#         schema = self.__getSchemaFromMetadataDict__('public_access_level')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationPublicAccessLevelBadValue(self):
#
#         data = {'public_access_level':'BadValue'
#         }
#         schema = self.__getSchemaFromMetadataDict__('public_access_level')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'public_access_level':[u'The input is not valid']})
#
#     def testFieldValidationPublicAccessLevelRejectsEmpty(self):
#
#         data = {'public_access_level':''
#         }
#         schema = self.__getSchemaFromMetadataDict__('public_access_level')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'public_access_level':[u'Missing value']})
#
#     def testFieldValidationPublicAccessLevelRejectsMissing(self):
#
#         data = {}
#         schema = self.__getSchemaFromMetadataDict__('public_access_level')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'public_access_level':[u'Missing value']})
#
#     ###### Field: publisher #####
#
#     def testFieldValidationPublisherBasic(self):
#
#         data = {'publisher':'an agency'
#         }
#         schema = self.__getSchemaFromMetadataDict__('publisher')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationPublisherNameTooLong(self):
#
#         data = {'publisher':'a'*301
#         }
#         schema = self.__getSchemaFromMetadataDict__('publisher')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'publisher':[u'Enter a value not more than 300 characters long']})
#
#     def testFieldValidationPublisherRejectsMissing(self):
#
#         data = {}
#         schema = self.__getSchemaFromMetadataDict__('publisher')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'publisher':[u'Missing value']})
#
#     def testFieldValidationPublisherRejectsEmpty(self):
#
#         data = {'publisher':''}
#         schema = self.__getSchemaFromMetadataDict__('publisher')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'publisher':[u'Missing value']})
#
#     ###### Field: contact_name #####
#
#     def testFieldValidationContactBasic(self):
#
#         data = {'contact_name':'jim'
#         }
#         schema = self.__getSchemaFromMetadataDict__('contact_name')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationContactNameTooLong(self):
#
#         data = {'contact_name':'a'*301
#         }
#         schema = self.__getSchemaFromMetadataDict__('contact_name')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'contact_name':[u'Enter a value not more than 300 characters long']})
#
#     def testFieldValidationContactRejectsMissing(self):
#
#         data = {}
#         schema = self.__getSchemaFromMetadataDict__('contact_name')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'contact_name':[u'Missing value']})
#
#     def testFieldValidationContactRejectsEmpty(self):
#
#         data = {'contact_name':''}
#         schema = self.__getSchemaFromMetadataDict__('contact_name')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'contact_name':[u'Missing value']})
#
#     ###### Field: contact_email #####
#
#     def testFieldValidationContactEmailBasic(self):
#
#         data = {'contact_email':'a@foo.me'
#         }
#         schema = self.__getSchemaFromMetadataDict__('contact_email')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationContactEmailTooLong(self):
#
#         data = {'contact_email':'a'*100+'@foo.com'
#         }
#         schema = self.__getSchemaFromMetadataDict__('contact_email')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'contact_email':[u'Enter a value not more than 100 characters long']})
#
#     def testFieldValidationContactEmailRejectsMissing(self):
#
#         data = {}
#         schema = self.__getSchemaFromMetadataDict__('contact_email')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'contact_email':[u'Missing value']})
#
#     def testFieldValidationContactEmailRejectsEmpty(self):
#
#         data = {'contact_email':''}
#         schema = self.__getSchemaFromMetadataDict__('contact_email')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'contact_email':[u'Missing value']})
#
#     ###### Field: unique_id #####
#     #TODO need test unique_id entered is verified to be unique for an organization
#
#     def testFieldValidationUIDBasic(self):
#
#         data = {'unique_id':'jim'
#         }
#         schema = self.__getSchemaFromMetadataDict__('unique_id')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationUIDTooLong(self):
#
#         data = {'unique_id':'a'*101
#         }
#         schema = self.__getSchemaFromMetadataDict__('unique_id')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'unique_id':[u'Enter a value not more than 100 characters long']})
#
#     def testFieldValidationUIDRejectsMissing(self):
#
#         data = {}
#         schema = self.__getSchemaFromMetadataDict__('unique_id')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'unique_id':[u'Missing value']})
#
#     def testFieldValidationUIDRejectsEmpty(self):
#
#         data = {'unique_id':''}
#         schema = self.__getSchemaFromMetadataDict__('unique_id')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'unique_id':[u'Missing value']})
#
#     ###### Field: data_dictionary #####
#
#     def testFieldValidationDataDictionaryBasic(self):
#
#         data = {'data_dictionary':'http://www.foo.com/my_data'
#         }
#         schema = self.__getSchemaFromMetadataDict__('data_dictionary')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationDataDictionaryBadURL(self):
#
#         data = {'data_dictionary':'wow this isnt a valid url'
#         }
#         schema = self.__getSchemaFromMetadataDict__('data_dictionary')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'data_dictionary':[u'That is not a valid URL']})
#
#     def testFieldValidationDataDictionaryTooLong(self):
#
#         data = {'data_dictionary': 'http://www.foo.com/'+('a'*350)
#         }
#         schema = self.__getSchemaFromMetadataDict__('data_dictionary')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'data_dictionary':[u'Enter a value not more than 350 characters long']})
#
#     def testFieldValidationDataDictionaryIgnoresMissing(self):
#
#         data = {}
#         schema = self.__getSchemaFromMetadataDict__('data_dictionary')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationDataDictionaryIgnoresEmpty(self):
#
#         data = {'data_dictionary':''}
#         schema = self.__getSchemaFromMetadataDict__('data_dictionary')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     ###### Field: endpoint #####
#
#     def testFieldValidationEndpointBasic(self):
#
#         data = {'endpoint':'http://www.foo.com/my_data'
#         }
#         schema = self.__getSchemaFromMetadataDict__('endpoint')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationEndpointBadURL1(self):
#
#         data = {'endpoint':'wow this isnt a valid url'
#         }
#         schema = self.__getSchemaFromMetadataDict__('endpoint')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'endpoint':[u'That is not a valid URL']})
#
#     def testFieldValidationEndpointBadURL2(self):
#
#         data = {'endpoint':'wowthisisntavalidurl'
#         }
#         schema = self.__getSchemaFromMetadataDict__('endpoint')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'endpoint':[u'You must provide a full domain name (like wowthisisntavalidurl.com)']})
#
#     def testFieldValidationEndpointTooLong(self):
#
#         data = {'endpoint': 'http://www.foo.com/'+('a'*350)
#         }
#         schema = self.__getSchemaFromMetadataDict__('endpoint')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'endpoint':[u'Enter a value not more than 350 characters long']})
#
#     def testFieldValidationEndpointIgnoresMissing(self):
#
#         data = {}
#         schema = self.__getSchemaFromMetadataDict__('endpoint')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationEndpointIgnoresEmpty(self):
#
#         data = {'endpoint':''}
#         schema = self.__getSchemaFromMetadataDict__('endpoint')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     ###### Field: spatial #####
#
#     def testFieldValidationSpatialTooLong(self):
#
#         data = {'spatial': 'a'*501
#         }
#         schema = self.__getSchemaFromMetadataDict__('spatial')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'spatial':[u'Enter a value not more than 500 characters long']})
#
#     def testFieldValidationSpatialIgnoresMissing(self):
#
#         data = {}
#         schema = self.__getSchemaFromMetadataDict__('spatial')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationSpatialIgnoresEmpty(self):
#
#         data = {'spatial':''}
#         schema = self.__getSchemaFromMetadataDict__('spatial')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     ###### Field: temporal #####
#
#     def testFieldValidationTemporalIgnoresMissing(self):
#
#         data = {}
#         schema = self.__getSchemaFromMetadataDict__('temporal')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationTemporalIgnoresEmpty(self):
#
#         data = {'temporal':''}
#         schema = self.__getSchemaFromMetadataDict__('temporal')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#         ###### Field: release_date #####
#
#     def testFieldValidationReleaseDateTooLong(self):
#
#         data = {'release_date': 'a'*501
#         }
#         schema = self.__getSchemaFromMetadataDict__('release_date')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'release_date':[u'Enter a value not more than 500 characters long']})
#
#     def testFieldValidationReleaseDateIgnoresMissing(self):
#
#         data = {}
#         schema = self.__getSchemaFromMetadataDict__('release_date')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationReleaseDateIgnoresEmpty(self):
#
#         data = {'release_date':''}
#         schema = self.__getSchemaFromMetadataDict__('release_date')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     ###### Field: accrual_periodicity #####
#
#     def testFieldValidationAccrualPeriodicityAcceptedValues(self):
#
#         schema = self.__getSchemaFromMetadataDict__('accrual_periodicity')
#
#         periods =  ["Annual", "Bimonthly", "Semiweekly", "Daily", "Biweekly", "Semiannual", "Biennial", "Triennial",
#                 "Three times a week", "Three times a month", "Continuously updated", "Monthly", "Quarterly", "Semimonthly",
#                 "Three times a year", "Weekly", "Completely irregular"]
#
#         for period in periods:
#             data = {'accrual_periodicity': period}
#             converted_data, errors = df.validate(data, schema)
#             self.assertEqual(errors, {})
#
#     def testFieldValidationAccrualPeriodicityInvalidValue(self):
#
#         data = {'accrual_periodicity': 'badvalue'
#         }
#         schema = self.__getSchemaFromMetadataDict__('accrual_periodicity')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'accrual_periodicity':[u'The input is not valid']})
#
#     def testFieldValidationAccrualPeriodicityIgnoresMissing(self):
#
#         data = {}
#         schema = self.__getSchemaFromMetadataDict__('accrual_periodicity')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationAccrualPeriodicityIgnoresEmpty(self):
#
#         data = {'accrual_periodicity':''}
#         schema = self.__getSchemaFromMetadataDict__('accrual_periodicity')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     ###### Field: language #####
#
#     def testFieldValidationLanguageIgnoresMissing(self):
#
#         data = {}
#         schema = self.__getSchemaFromMetadataDict__('language')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationLanguageIgnoresEmpty(self):
#
#         data = {'language':''}
#         schema = self.__getSchemaFromMetadataDict__('language')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationLanguageAllowsCommaSeparated(self):
#
#         data = {'language':'es-MX, wo, nv,   en-US'}
#         schema = self.__getSchemaFromMetadataDict__('language')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     ###### Field: bureau code #####
#     def testFieldValidationBureauCodeInvalid1(self):
#
#         data = {'bureau_code': '000:1111'
#         }
#         schema = self.__getSchemaFromMetadataDict__('bureau_code')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'bureau_code':[u'The input is not valid']})
#
#     def testFieldValidationBureauCodeInvalid2(self):
#
#         data = {'bureau_code': '000:1'
#         }
#         schema = self.__getSchemaFromMetadataDict__('bureau_code')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'bureau_code':[u'The input is not valid']})
#
#     def testFieldValidationBureauCodeValid(self):
#
#         data = {'bureau_code': '000:11'
#         }
#         schema = self.__getSchemaFromMetadataDict__('bureau_code')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationBureauCodeIgnoresMissing(self):
#
#         data = {}
#         schema = self.__getSchemaFromMetadataDict__('bureau_code')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationBureauCodeAllowsCommaSeparated(self):
#
#         data = {
#             'bureau_code': '000:11,111:00,333:23'
#         }
#         schema = self.__getSchemaFromMetadataDict__('bureau_code')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationBureauCodeAllowsCommaSeparatedSpaces(self):
#
#         data = {
#             'bureau_code': '000:11, 111:00 , 333:23'
#         }
#         schema = self.__getSchemaFromMetadataDict__('bureau_code')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationBureauCodeIgnoresEmpty(self):
#
#         data = {'bureau_code':''}
#         schema = self.__getSchemaFromMetadataDict__('bureau_code')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     ###### Field: program code #####
#     def testFieldValidationProgramCodeInvalid1(self):
#
#         data = {'program_code': '000:1111'
#         }
#         schema = self.__getSchemaFromMetadataDict__('program_code')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'program_code':[u'The input is not valid']})
#
#     def testFieldValidationProgramCodeInvalid2(self):
#
#         data = {'program_code': '000:11'
#         }
#         schema = self.__getSchemaFromMetadataDict__('program_code')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'program_code':[u'The input is not valid']})
#
#     def testFieldValidationProgramCodeValid(self):
#
#         data = {'program_code': '000:111'
#         }
#         schema = self.__getSchemaFromMetadataDict__('program_code')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationProgramCodeIgnoresMissing(self):
#
#         data = {}
#         schema = self.__getSchemaFromMetadataDict__('program_code')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationProgramCodeIgnoresEmpty(self):
#
#         data = {'program_code':''}
#         schema = self.__getSchemaFromMetadataDict__('program_code')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationProgramCodeAllowsCommaSeparated(self):
#
#         data = {
#             'program_code': '000:110,111:001,333:233'
#         }
#         schema = self.__getSchemaFromMetadataDict__('program_code')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationProgramCodeAllowsCommaSeparatedSpaces(self):
#
#         data = {
#             'program_code': '000:111, 111:003 , 333:232'
#         }
#         schema = self.__getSchemaFromMetadataDict__('program_code')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     ###### Field: access level comment #####
#     def testFieldValidationAccessLevelCommentTooLong(self):
#
#         data = {'access_level_comment': 'a'*256 }
#         schema = self.__getSchemaFromMetadataDict__('access_level_comment')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'access_level_comment':[u'Enter a value not more than 255 characters long']})
#
#     def testFieldValidationAccessLevelCommentIgnoresMissing(self):
#
#         data = {}
#         schema = self.__getSchemaFromMetadataDict__('access_level_comment')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationAccessLevelCommentIgnoresEmpty(self):
#
#         data = {'access_level_comment':''}
#         schema = self.__getSchemaFromMetadataDict__('access_level_comment')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     ###### Field: primary it investment uii #####
#     def testFieldValidationInvestmentUIITooLong(self):
#
#         data = {'primary_it_investment_uii': 'a'*256 }
#         schema = self.__getSchemaFromMetadataDict__('primary_it_investment_uii')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {'primary_it_investment_uii':[u'Enter a value not more than 75 characters long']})
#
#     def testFieldValidationInvestmentUIIIgnoresMissing(self):
#
#         data = {}
#         schema = self.__getSchemaFromMetadataDict__('primary_it_investment_uii')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     def testFieldValidationInvestmentUIIIgnoresEmpty(self):
#
#         data = {'primary_it_investment_uii':''}
#         schema = self.__getSchemaFromMetadataDict__('primary_it_investment_uii')
#
#         converted_data, errors = df.validate(data, schema)
#         self.assertEqual(errors, {})
#
#     ###### Utility methods #####
#     @classmethod
#     def __getSchemaFromMetadataDict__(cls, id_value):
#         """Convenience function to extract the schema for a given field"""
#         for scheme in plugin.required_metadata+plugin.required_if_applicable_metadata+plugin.expanded_metadata:
#             if scheme['id'] == id_value:
#                 return {scheme['id']:scheme['validators']}
#         return {}
#
#     @classmethod
#     def __check_dicts_match__(cls, dict1, dict2):
#         """helper function to compare two dicts to ensure that they match"""
#         assert set(dict1) - set(dict2) == set([])
#         assert set(dict2) - set(dict1) == set([])
