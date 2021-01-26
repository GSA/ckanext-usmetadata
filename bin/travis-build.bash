#!/bin/bash
set -e

echo "This is travis-build.bash..."

echo "Installing the packages that CKAN requires..."
sudo apt-get update -qq
sudo apt-get install postgresql postgresql-contrib solr-jetty libcommons-fileupload-java libpq-dev swig

pip install pip==20.3.3
pip install testrepository

echo "Installing CKAN and its Python dependencies..."
git clone https://github.com/gsa/ckan
cd ckan
if [ $CKANVERSION == 'inventory' ]
then
	git checkout inventory
elif [ $CKANVERSION == '2.2' ]
then
	git checkout release-v2.2.3
fi
python setup.py develop
cp ./ckan/public/base/css/main.css ./ckan/public/base/css/main.debug.css
pip install -r requirements.txt
pip install -r dev-requirements.txt
cd -

echo "Creating the PostgreSQL user and database..."
sudo -u postgres psql -c "CREATE USER ckan_default WITH PASSWORD 'pass';"
sudo -u postgres psql -c 'CREATE DATABASE ckan_test WITH OWNER ckan_default;'
sudo -u postgres psql -c 'CREATE DATABASE datastore_test WITH OWNER ckan_default;'

#echo "Initialising the database..."
#cd ckan
#paster db init -c test-core.ini
#cd -

echo "Installing ckanext-pages and its requirements..."
python setup.py develop
#pip install -r dev-requirements.txt

echo "Moving test.ini into a subdir..."
mkdir subdir
mv test.ini subdir

echo "travis-build.bash is done."
