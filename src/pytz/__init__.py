#!/usr/bin/env python
'''
$Id: __init__.py,v 1.1 2004/06/05 09:53:55 zenzen Exp $

datetime.tzinfo timezone definitions generated from the
Olson timezone database:

    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz

See the datetime section of the Python Library Reference for information
on how to use these modules.
'''

__rcs_id__  = '$Id: __init__.py,v 1.1 2004/06/05 09:53:55 zenzen Exp $'
__version__ = '$Revision: 1.1 $'[11:-2]

# The Olsen database has historically been updated about 4 times a year
OLSEN_VERSION = '2004a'

__all__ = ['timezone', 'all_timezones', 'common_timezones']

import sys

def timezone(zone):
    ''' Return a datetime.tzinfo implementation for the given timezone '''
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

    # Return class from that module
    rv = getattr(rv, zone_bits[-1])
    assert type(rv) != type(sys)
    return rv

def _munge_zone(zone):
    ''' Convert a zone into a string suitable for use as a Python identifier 
    '''
    return zone.replace('+', '_plus_').replace('-', '_minus_')


