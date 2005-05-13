#!/usr/bin/env python
'''
$Id: __init__.py,v 1.12 2005/02/15 20:21:41 zenzen Exp $

datetime.tzinfo timezone definitions generated from the
Olson timezone database:

    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz

See the datetime section of the Python Library Reference for information
on how to use these modules.
'''

# The Olson database has historically been updated about 4 times a year
OLSON_VERSION = '2005i'
VERSION = OLSON_VERSION
#VERSION = OLSON_VERSION + '.2'

OLSEN_VERSION = OLSON_VERSION # Old releases had this misspelling

__all__ = ['timezone', 'all_timezones', 'common_timezones', 'utc']

import sys, datetime

from tzinfo import AmbiguousTimeError

ZERO = datetime.timedelta(0)
HOUR = datetime.timedelta(hours=1)

# A UTC class.

class UTC(datetime.tzinfo):
    """UTC
    
    Identical to the reference UTC implementation given in Python docs except
    that it unpickles using the single module global instance defined beneath
    this class declaration.
    """

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO
    
    def __reduce__(self):
        return _UTC, ()

    def localize(self, dt, is_dst=False):
        '''Convert naive time to local time'''
        if dt.tzinfo is not None:
            raise ValueError, 'Not naive datetime (tzinfo is already set)'
        return dt.replace(tzinfo=self)

    def normalize(self, dt, is_dst=False):
        '''Correct the timezone information on the given datetime'''
        if dt.tzinfo is None:
            raise ValueError, 'Naive time - no tzinfo set'
        return dt.replace(tzinfo=self)

    def __repr__(self):
        return '<UTC>'


UTC = utc = UTC()

def _UTC():
    """Factory function for utc unpickling.
    
    Makes sure that unpickling a utc instance always returns the same 
    module global.
    
    These examples belong in the UTC class above, but it is obscured; or in
    the README.txt, but we are not depending on Python 2.4 so integrating
    the README.txt examples with the unit tests is not trivial.
    
    >>> import datetime, pickle
    >>> dt = datetime.datetime(2005, 3, 1, 14, 13, 21, tzinfo=utc)
    >>> naive = dt.replace(tzinfo=None)
    >>> p = pickle.dumps(dt, 1)
    >>> naive_p = pickle.dumps(naive, 1)
    >>> len(p), len(naive_p), len(p) - len(naive_p)
    (60, 43, 17)
    >>> new = pickle.loads(p)
    >>> new == dt
    True
    >>> new is dt
    False
    >>> new.tzinfo is dt.tzinfo
    True
    >>> utc is UTC is timezone('UTC')
    True
    >>> utc is timezone('GMT')
    False
    """
    return utc
_UTC.__safe_for_unpickling__ = True

def timezone(zone):
    ''' Return a datetime.tzinfo implementation for the given timezone 
    
    >>> from datetime import datetime, timedelta
    >>> utc = timezone('UTC')
    >>> eastern = timezone('US/Eastern')
    >>> eastern.zone
    'US/Eastern'
    >>> utc_dt = datetime(2002, 10, 27, 6, 0, 0, tzinfo=utc)
    >>> loc_dt = utc_dt.astimezone(eastern)
    >>> fmt = '%Y-%m-%d %H:%M:%S %Z (%z)'
    >>> loc_dt.strftime(fmt)
    '2002-10-27 01:00:00 EST (-0500)'
    >>> (loc_dt - timedelta(minutes=10)).strftime(fmt)
    '2002-10-27 00:50:00 EST (-0500)'
    >>> eastern.normalize(loc_dt - timedelta(minutes=10)).strftime(fmt)
    '2002-10-27 01:50:00 EDT (-0400)'
    >>> (loc_dt + timedelta(minutes=10)).strftime(fmt)
    '2002-10-27 01:10:00 EST (-0500)'
    '''
    zone = _munge_zone(zone)
    if zone.upper() == 'UTC':
        return utc
    zone_bits = ['zoneinfo'] + zone.split('/')

    # Load zone's module
    module_name = '.'.join(zone_bits)
    try:
        module = __import__(module_name, globals(), locals())
    except ImportError:
        raise KeyError, zone
    rv = module
    for bit in zone_bits[1:]:
        rv = getattr(rv, bit)

    # Return instance from that module
    rv = getattr(rv, zone_bits[-1])
    assert type(rv) != type(sys)
    return rv

def _munge_zone(zone):
    ''' Convert a zone into a string suitable for use as a Python identifier 
    '''
    return zone.replace('+', '_plus_').replace('-', '_minus_')

def _test():
    import doctest, os, sys
    sys.path.insert(0, os.pardir)
    import pytz
    return doctest.testmod(pytz)

if __name__ == '__main__':
    _test()

