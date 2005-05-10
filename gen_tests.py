#!/usr/bin/env python
# -*- coding: ascii -*-
'''
$Id: gen_tests.py,v 1.2 2004/05/31 20:44:35 zenzen Exp $
'''

__rcs_id__  = '$Id: gen_tests.py,v 1.2 2004/05/31 20:44:35 zenzen Exp $'
__version__ = '$Revision: 1.2 $'[11:-2]

import os, os.path, popen2, re
from gen_tzinfo import allzones

zdump = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'build','etc','zdump'
        ))

def main():
    dest_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'build', 'tz')
            )
    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir)
    
    outf_name = os.path.join(dest_dir, 'test_zdump.py')
    outf = open(outf_name, 'w')
    print >> outf, """
#!/usr/bin/env python

import sys, os
sys.path.insert(0, os.pardir)
from time import strptime
from __init__ import timezone

from datetime import tzinfo, timedelta, datetime

def test():
    '''
    Daylight savings time transition tests generated from the Olsen
    timezone database using the reference zdump implementation.
    
    """

    for zone in allzones():
        zd_out, zd_in = popen2.popen2('%s -v %s' % (zdump, zone))
        zd_in.close()
        lines = zd_out.readlines()
        for idx in range(0, len(lines)):
            line = lines[idx]
            #if '2002' not in line:
            #    continue
            m = re.match(
                '^([^\s]+) \s+ (.* \s UTC) \s+=\s+ (.*)\s(\w+) \s+isdst=(0|1)$',
                line, re.X
                )
            if m:
                zone, utc_string, local_string, tzname, is_dst = m.groups()
            else:
                raise RuntimeError, 'Dud line %r' % (line,)

            # Get the next line, so we can fix the timezone acronym
            # if necessary to match Python's end-of-dst behavior
            try:
                nline = lines[idx+1]
            except IndexError:
                nline = lines[idx-2]
            m = re.match(
                '^([^\s]+) \s+ (.* \s UTC) \s+=\s+ (.*)\s(\w+) \s+isdst=(0|1)$',
                nline, re.X
                )
            if m:
                nzone, nutc_string, nlocal_string, ntzname, nis_dst = m.groups()
            else:
                raise RuntimeError, 'Dud line %r' % (nline,)

            if int(is_dst) and not int(nis_dst):
                tzname = ntzname

            # Add leading 0 to single character day of month
            if local_string[8] == ' ':
                local_string = local_string[:8] + '0' + local_string[9:]
            local_string = '%s %s' % (local_string, tzname)

            print >> outf, '    >>> aszone(%s, %s)' % (
                    repr(utc_string), repr(zone)
                    )
            print >> outf, '   ',
            print >> outf, repr(local_string)
            print >> outf
    

    print >> outf, """
    '''

ZERO = timedelta(0)
class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return 'UTC'

    def dst(self, dt):
        return ZERO
utc_tz = UTC()

def aszone(utc_string, zone):
    loc_tz = timezone(zone)
    utc_t = strptime(utc_string, '%a %b %d %H:%M:%S %Y UTC')[:6] + (0, utc_tz)
    utc_datetime = datetime(*utc_t)
    loc_datetime = utc_datetime.astimezone(loc_tz)
    return '%s' % (loc_datetime.strftime('%a %b %d %H:%M:%S %Y %Z'))

def _test():
    import doctest, test_zdump
    return doctest.testmod(test_zdump)

if __name__ == '__main__':
    _test()
"""

if __name__ == '__main__':
    main()

# vim: set filetype=python ts=4 sw=4 et

