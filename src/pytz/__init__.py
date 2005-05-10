#!/usr/bin/env python
'''
$Id: __init__.py,v 1.11 2005/01/07 04:51:33 zenzen Exp $

datetime.tzinfo timezone definitions generated from the
Olson timezone database:

    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz

See the datetime section of the Python Library Reference for information
on how to use these modules.
'''

__rcs_id__  = '$Id: __init__.py,v 1.11 2005/01/07 04:51:33 zenzen Exp $'
__version__ = '$Revision: 1.11 $'[11:-2]

# The Olson database has historically been updated about 4 times a year
OLSON_VERSION = '2005a'
VERSION = OLSON_VERSION
#VERSION = OLSON_VERSION + '.2'

OLSEN_VERSION = OLSON_VERSION # Old releases had this misspelling

__all__ = ['timezone', 'all_timezones', 'common_timezones']

import sys

from tzinfo import AmbiguousTimeError

def timezone(zone):
    ''' Return a datetime.tzinfo implementation for the given timezone 
    
    >>> from datetime import datetime, timedelta
    >>> utc = timezone('UTC')
    >>> eastern = timezone('US/Eastern')
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

