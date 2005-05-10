#!/usr/bin/env python
'''
$Id: __init__.py,v 1.2 2003/08/06 16:34:10 zenzen Exp $

This package contains tzinfo timezone definitions generated from the
Olson timezone database:

    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz

See the datetime section of the Python Library Reference for information
on how to use these modules.
'''

__rcs_id__  = '$Id: __init__.py,v 1.2 2003/08/06 16:34:10 zenzen Exp $'
__version__ = '$Revision: 1.2 $'[11:-2]

__all__ = ['timezone']

import sys

def timezone(zone):
    ''' Return a datetime.tzinfo implementation for the given timezone '''
    zone_bits = zone.split('/')
    module_name = '.'.join(zone_bits)
    try:
        module = __import__(module_name, globals(), locals())
    except ImportError:
        raise KeyError, zone
    rv = getattr(module, zone_bits[-1])
    if type(rv) == type(sys):
        rv = getattr(rv, zone_bits[-1])
    return rv

