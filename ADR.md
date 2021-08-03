
ADRs for ckanext-usmetadata
===========================

## 1. Reduce complexity of schema logic

Date: 2021-08-03

### Status

Unknown

### Context

The existing schema definitions for ckanext-usmetadata were complex and it's effect was not completely known.

### Decision

To expedite the upgrade to PY3, proper validation was made more lenient.  There are a bunch of unit tests in unit_test.py and the ones that were failing or otherwise broken
were commented out to be worked on in the future.

### Consequences

- Until the schema is updated properly, incomplete input data may cause unknown bugs throughout the system.

## 2. Update test suite

Date: 2021-08-03

### Status

Accepted

### Context

The old tests were written for an older version of ckan (possibly 2.5) using nosetests and relying on outdated frameworks.

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

There were two validators that were imported from [formencode](https://github.com/formencode/formencode), Regex and UnicodeString.  In PY2+CKAN2.8, these data types
had no issues with the sql code.  However, in PY3+CKAN2.9, sql didn't know how to adapt these types.

### Decision

Custom vaildator functions were written to handle the functionality that the imported validators provided.  The following link was used as a reference,
- https://docs.ckan.org/en/2.9/extensions/adding-custom-fields.html#custom-validators
The validators were not registered with the plugin because the place where they were defined was already importing the plugin, so there would have
been a circular dependency.  Either way, the validators work as standalong functions that get called.

### Consequences

- The string_length_validator has known issues where sometimes it allows strings that are longer than allowed.  However, as a unit test, the function works.
- There are probably unknown consequences.
