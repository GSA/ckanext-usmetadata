# ckanext-usmetadata

![Github Actions](https://github.com/GSA/ckanext-usmetadata/actions/workflows/test.yml/badge.svg)

This CKAN Extension expands CKAN to offer a number of custom fields related to the [DCAT-US Schema](https://resources.data.gov/schemas/dcat-us/v1.1/)

### Installation

To install this package, activate CKAN virtualenv (e.g. "source /path/to/virtenv/bin/activate"), then run


    (virtenv) 'pip install -e git+https://github.com/gsa/usmetadata#egg=ckanext-usmetadata'
    (virtenv) 'python setup.py develop'
    
Then in your CKAN .ini file, add `usmetadata`
to your ckan.plugins line:

	ckan.plugins = (other plugins here...) usmetadata

### Requirements

This extension is compatible with these versions of CKAN.

CKAN version | Compatibility
------------ | -------------
<=2.7        | no
2.8          | yes
2.9          | [in progress](https://github.com/GSA/datagov-ckan-multi/issues/581)

### Development

You may also install by cloning the git repo, then running ''python setup.py develop'' from the root of your source
directory, which will install an egg link so that you can modify the code and see results without reinstalling

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

In order to support multiple versions of CKAN, or even upgrade to new versions
of CKAN, we support development and testing through the `CKAN_VERSION`
environment variable.

    $ make CKAN_VERSION=2.8 test
    $ make CKAN_VERSION=2.9 test
    
## Credit / Copying

Credit to the original owner of the repo.  Everything here is built on top of the original foundation.
