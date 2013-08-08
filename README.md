This CKAN Extension expands CKAN to offer a number of custom fields related to the "US Common Core Schema":http://project-open-data.github.io/schema/

Installation
============

To install this package, from your CKAN virtualenv, run the following from your CKAN base folder (e.g. ``pyenv/``)::

  pip install -e git+https://github.com/seanherron/usmetadata#egg=ckanext-usmetadata

Then activate it by setting ``ckan.plugins = usmetadata`` in your main ``ini``-file.