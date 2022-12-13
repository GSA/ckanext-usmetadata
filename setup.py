from setuptools import setup, find_packages
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ckanext-usmetadata',
    version='0.2.5',
    description='US Metadata Plugin for CKAN',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3'
    ],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Data.gov',
    author_email='datagovhelp@gsa.gov',
    url='https://github.com/GSA/ckanext-usmetadata',
    license='Public Domain',
    packages=find_packages(),
    namespace_packages=['ckanext', 'ckanext.usmetadata'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    setup_requires=['wheel'],
    entry_points="""
        [ckan.plugins]
            usmetadata=ckanext.usmetadata.plugin:CommonCoreMetadataFormPlugin
    """,
)
