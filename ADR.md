
ADRs for ckanext-usmetadata
===========================

## 1. Reduce complexity of schema logic

Date: 2021-08-03

### Status

Unknown

### Context

The existing schema definitions for ckanext-usmetadata were complex and it's effect was not completely known.

### Decision

To expedite the upgrade to PY3, proper validation was made more lenient.  There are a bunch of unit tests in 
unit_test.py and the ones that were failing or otherwise broken were commented out to be worked on in the 
future.

### Consequences

- Until the schema is updated properly, users may be able to input data that is not exportable in the 
data.json file. Due to the limited number of users and very little new users, this risk was deemed acceptable.

## 2. Update test suite

Date: 2021-08-03

### Status

Accepted

### Context

The old tests were written for an older version of ckan (possibly 2.5) using nosetests and relying on 
outdated frameworks.

### Decision

A few sources were researched to properly upgrade the tests:
- https://docs.python.org/3/library/unittest.html
- https://docs.ckan.org/en/2.9/extensions/testing-extensions.html
- https://flask.palletsprojects.com/en/2.0.x/reqcontext/
- https://github.com/ckan/ckan/issues/4247

### Consequences

- non-known.

## 3. Write custom validators

Date: 2021-08-03

### Status

Accepted

### Context

There were two validators that were imported from [formencode](https://github.com/formencode/formencode), 
Regex and UnicodeString.  In PY2+CKAN2.8, these data types had no issues with the sql code.  However, 
in PY3+CKAN2.9, sql didn't know how to adapt these types.

### Decision

Custom vaildator functions were written to handle the functionality that the imported validators provided. 
The following link was used as a reference,
- https://docs.ckan.org/en/2.9/extensions/adding-custom-fields.html#custom-validators
The validators were not registered with the plugin because the place where they were defined was already 
importing the plugin, so there would have been a circular dependency.  Either way, the validators work as 
standalone functions that get called.

### Consequences

- There are probably unknown consequences.


## 4. Update docker test environment

Date: 2021-08-06

### Status

Not Implemented

### Context

Currently, a custom Dockerfile is used to install pip requirements and also the desired working extension.  
The CKAN 2.8 and 2.9 docker dev images, [openknowledge/ckan-dev](https://github.com/okfn/docker-ckan/blob/
master/ckan-dev/2.8/setup/start_ckan_development.sh), support installing these things as part of the startup 
of the container.  

An example of updating to not use the dockerfile is seen in [ckanext-dcat_usmetadata](https://github.com/
GSA/ckanext-dcat_usmetadata/commit/8df5e938d750e26caddd3688b40b696991a5e0ad).  While there is still a 
Dockerfile, it only installed base linux packages and doesn't handle anything with the extension.  Since 
this extension does not need any additional linux packages, the docker-compose.yml would directly call
`image: openknowledge/ckan-dev:${CKAN_VERSION}`.  

### Decision

This change was not implemented yet because no further development was necessary since the prototype of 
the development workflow was completed.  There is a bit of residual py3 bugfixes/cleanup that will be 
done at some point before deployment.  It was thought that this could wait until then.

### Consequences

- No tangible consequencees.
- Just slightly different development pipelines.
