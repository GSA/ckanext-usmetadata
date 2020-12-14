from formencode import Invalid
from ckanext.usmetadata.plugin import expanded_metadata


def validate(sid, values):
    """ test accrual_periodicity values """

    for em in expanded_metadata:
        if em['id'] == sid:
            validators = em['validators']

    for test in values:
        for validator in validators:
            # if fails will raise an error
            print "validating {} for {} at {}".format(test, sid, validator)
            try:
                validator.to_python(test)
                print " - OK {} for {} at {}".format(test, sid, validator)
            except AttributeError:  # it's a simple function validator
                pass  # extra validation functions
            except Invalid:
                print " - INVALID {} for {} at {}".format(test, sid, validator)
                raise


def test_accrual_periodicity():
    tests = [
        'Annual',
        'monthly',
        'R/P3Y6M4DT12H30M5S',
        'R/P1Y2DT3M',
        'R/P1Y2D']
    validate('accrual_periodicity', tests)


def test_release_date():
    validate('release_date', ['2020-10-01'])


def test_language():
    validate('language', ['en', 'es'])
