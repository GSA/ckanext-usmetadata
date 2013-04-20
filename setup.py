from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
        name='ckanext-usmetadata',
        version=version,
        description="Adds US metadata schema fields.",
        long_description="""\
        """,
        classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        keywords='',
        author='Marina Martin',
        author_email='marina@marinamartin.com',
        url='http://data.gov',
        license='GPL',
        packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
        namespace_packages=['ckanext', 'ckanext.usmetadata'],
        include_package_data=True,
        zip_safe=False,
        install_requires=[
                # -*- Extra requirements: -*-
        ],
        entry_points=\
        """
        [ckan.plugins]
        # Add plugins here, eg
        # myplugin=ckanext.usmetadata:PluginClass
        """,
)


