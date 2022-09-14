from __future__ import print_function
from ckan.lib.navl.dictization_functions import Invalid
from ckanext.usmetadata.helper import expanded_metadata, \
    release_date_validator, accrual_periodicity_validator, language_validator


def validate(sid, values):
    """ test accrual_periodicity values """

    for em in expanded_metadata:
        if em['id'] == sid:
            validators = em['validators']

    ok = []
    failed = []
    for test in values:
        for validator in validators:
            # if fails will raise an error
            print("validating {} for {} at {}".format(test, sid, validator))
            try:
                if validator in [release_date_validator, accrual_periodicity_validator, language_validator]:
                    valid = validator(test)
                    if type(valid) != Invalid:
                        print(" - OK {} for {} at {}".format(test, sid, validator))
                        ok.append(test)
                    else:
                        print(" - INVALID {} for {} at {}".format(test, sid, validator))
                        failed.append(test)
                else:
                    validator.to_python(test)
                    print(" - OK {} for {} at {}".format(test, sid, validator))
                    ok.append(test)
            except AttributeError:  # it's a simple function validator
                pass  # extra validation functions

    return ok, failed


def test_accrual_periodicity():
    tests = [
        'Annual',
        'monthly',
        'R/P3Y6M4DT12H30M5S',
        'R/P1Y2DT3M',
        'R/P1Y2D',
        'Not exists']
    ok, failed = validate('accrual_periodicity', tests)
    assert failed == ['Not exists']
    assert len(ok) == 5


def test_release_date():
    ok, failed = validate('release_date', ['2020-10-01', '33/92/3000'])
    assert failed == ['33/92/3000']
    assert '2020-10-01' in ok


def test_language():
    ok, failed = validate('language', ['en', 'es', 'notexists'])
    assert failed == ['notexists']
    assert len(ok) == 2
