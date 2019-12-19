[![Build Status](https://travis-ci.org/GSA/USMetadata.svg?branch=develop)](https://travis-ci.org/GSA/USMetadata)
[![Coverage Status](https://coveralls.io/repos/GSA/USMetadata/badge.svg?branch=develop&service=github)](https://coveralls.io/github/GSA/USMetadata?branch=develop)

This CKAN Extension expands CKAN to offer a number of custom fields related to the [US Common Core Schema](http://project-open-data.github.io/schema/)

Installation
============

To install this package, activate CKAN virtualenv (e.g. "source /path/to/virtenv/bin/activate"), then run


    (virtenv) 'pip install -e git+https://github.com/ljpetrova/usmetadata#egg=ckanext-usmetadata'
    (virtenv) 'python setup.py develop'
Then activate it by adding "usmetadata" to "ckan.plugins" in your main "ini"-file.

Tests
=====

    nosetests --ckan --nologcapture --with-pylons=test.ini --reset-db --with-coverage --cover-package=ckanext.usmetadata --cover-inclusive --cover-erase --cover-tests

Development
============
You may also install by cloning the git repo, then running ''python setup.py develop'' from the root of your source
directory, which will install an egg link so that you can modify the code and see results without reinstalling
