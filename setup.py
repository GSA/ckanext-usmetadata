from setuptools import setup, find_packages

version = '0.2.1'

setup(
	name='ckanext-usmetadata',
	version=version,
	description='US Metadata Plugin',
	long_description='',
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Sean Herron, created by Marina Martin',
	author_email='sean.herron@fda.hhs.gov',
	url='',
	license='',
	packages=find_packages(),
	namespace_packages=['ckanext', 'ckanext.usmetadata'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[],
	entry_points=\
	"""
        [ckan.plugins]
	    usmetadata=ckanext.usmetadata.plugin:CommonCoreMetadataFormPlugin
	""",
)
