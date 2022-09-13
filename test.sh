#!/bin/bash
# Setup and run extension tests. This script should be run in a _clean_ CKAN
# environment. e.g.:
#
#     $ docker-compose run --rm app ./test.sh
#

set -o errexit
set -o pipefail

# Database is listening, but still unavailable. Just keep trying...
while ! ckan -c /app/test.ini db init; do 
  echo Retrying in 5 seconds...
  sleep 5
done

pytest --ckan-ini=/app/test.ini --cov=ckanext.usmetadata --disable-warnings /app/ckanext/usmetadata/tests/
