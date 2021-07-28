[![CircleCI](https://circleci.com/gh/GSA/ckanext-usmetadata.svg?style=svg)](https://circleci.com/gh/GSA/ckanext-usmetadata)


This CKAN Extension expands CKAN to offer a number of custom fields related to the [DCAT-US Schema](https://resources.data.gov/schemas/dcat-us/v1.1/)

Installation
============

To install this package, activate CKAN virtualenv (e.g. "source /path/to/virtenv/bin/activate"), then run


    (virtenv) 'pip install -e git+https://github.com/gsa/usmetadata#egg=ckanext-usmetadata'
    (virtenv) 'python setup.py develop'


Then activate it by adding "usmetadata" to "ckan.plugins" in your main "ini"-file.

Development
==============

### Setup

Build the docker containers.

    $ make build

Start the docker containers.

    $ make up

CKAN will start at [localhost:5000](http://localhost:5000/).

Clean up any containers and volumes.

    $ make down

Open a shell to run commands in the container.

    $ docker-compose exec ckan bash

If you're unfamiliar with docker-compose, see our
[cheatsheet](https://github.com/GSA/datagov-deploy/wiki/Docker-Best-Practices#cheatsheet)
and the [official docs](https://docs.docker.com/compose/reference/).

For additional make targets, see the help.

    $ make help


### Testing

They follow the guidelines for [testing CKAN
extensions](https://docs.ckan.org/en/2.8/extensions/testing-extensions.html#testing-extensions).

To run the extension tests, start the containers with `make up`, then:

    $ make test

Lint the code.

    $ make lint


### Matrix builds

The existing development environment assumes a full catalog.data.gov test setup. This makes
it difficult to develop and test against new versions of CKAN (or really any
dependency) because everything is tightly coupled and would require us to

Development
============
You may also install by cloning the git repo, then running ''python setup.py develop'' from the root of your source
directory, which will install an egg link so that you can modify the code and see results without reinstalling
