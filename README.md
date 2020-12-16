[![CircleCI](https://circleci.com/gh/GSA/USMetadata.svg?style=svg)](https://circleci.com/gh/GSA/USMetadata)


This CKAN Extension expands CKAN to offer a number of custom fields related to the [DCAT-US Schema](https://resources.data.gov/schemas/dcat-us/v1.1/)

Installation
============

To install this package, activate CKAN virtualenv (e.g. "source /path/to/virtenv/bin/activate"), then run


    (virtenv) 'pip install -e git+https://github.com/gsa/usmetadata#egg=ckanext-usmetadata'
    (virtenv) 'python setup.py develop'
Then activate it by adding "usmetadata" to "ckan.plugins" in your main "ini"-file.

Tests
=====

    nosetests --ckan --nologcapture --with-pylons=test.ini --reset-db --with-coverage --cover-package=ckanext.usmetadata --cover-inclusive --cover-erase --cover-tests

Development
============
You may also install by cloning the git repo, then running ''python setup.py develop'' from the root of your source
directory, which will install an egg link so that you can modify the code and see results without reinstalling
