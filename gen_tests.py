#!/usr/bin/env python
# -*- coding: ascii -*-
'''
$Id: gen_tests.py,v 1.6 2004/06/03 00:15:24 zenzen Exp $
'''

__rcs_id__  = '$Id: gen_tests.py,v 1.6 2004/06/03 00:15:24 zenzen Exp $'
__version__ = '$Revision: 1.6 $'[11:-2]

import os, os.path, popen2, re, sys
from gen_tzinfo import allzones
import gen_tzinfo

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
'''
Daylight savings time transition tests generated from the Olsen
timezone database using the reference zdump implementation.
'''
    
import sys, os
sys.path.insert(0, os.pardir)
from time import strptime
from __init__ import timezone

from datetime import tzinfo, timedelta, datetime
    """

    for zone in allzones():
        tname = zone.replace(
                '+', '_plus_').replace('-', '_minus_').replace('/','_')
        print >> outf, '\ndef test_%s():' % tname
        print >> outf, "    '''"
        zd_out, zd_in = popen2.popen2('%s -v %s' % (zdump, zone))
        zd_in.close()
        lines = zd_out.readlines()
        for idx in range(0, len(lines)):
            line = lines[idx]
            #if '2002' not in line:
            #    continue
            m = re.match(
                '^([^\s]+)\s+(.+\sUTC) \s+=\s+ (.+)\s([^\s]+) \s+isdst=(0|1)$',
                line, re.X
                )
            if m:
                zone, utc_string, local_string, tzname, is_dst = m.groups()
            else:
                raise RuntimeError, 'Dud line %r' % (line,)

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
        print >> outf, "    '''"
    

    print >> outf, """

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
    try:
        gen_tzinfo.target = sys.argv[1:]
    except IndexError:
        gen_tzinfo.target = None
    main()

# vim: set filetype=python ts=4 sw=4 et

