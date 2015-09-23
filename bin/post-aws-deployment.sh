#!/usr/bin/env bash
. /usr/lib/ckan/default/bin/activate
pip install -e /usr/lib/ckan/default/src/ckanext-usmetadata
python /usr/lib/ckan/default/src/ckanext-usmetadata/setup.py develop
touch /etc/ckan/apache.wsgi