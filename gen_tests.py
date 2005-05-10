#!/usr/bin/env python
# -*- coding: ascii -*-
'''
$Id: gen_tests.py,v 1.13 2004/07/24 18:05:54 zenzen Exp $
'''

__rcs_id__  = '$Id: gen_tests.py,v 1.13 2004/07/24 18:05:54 zenzen Exp $'
__version__ = '$Revision: 1.13 $'[11:-2]

import os, os.path, popen2, re, sys
from gen_tzinfo import allzones
import gen_tzinfo
from time import strptime
from datetime import datetime, timedelta

zdump = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'build','etc','zdump'
        ))

def main():
    dest_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'build', 'dist')
            )
    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir)
    
    outf_name = os.path.join(dest_dir, 'test_zdump.py')
    outf = open(outf_name, 'w')
    print >> outf, """\
#!/usr/bin/env python
'''
Daylight savings time transition tests generated from the Olsen
timezone database using the reference zdump implementation.
'''
    
import unittest
from time import strptime
from pytz import timezone

from datetime import tzinfo, timedelta, datetime
    """

    for zone in allzones():
        print 'Generating test for %s in test_zdump.py' % (zone,)
        tname = zone.replace(
                '+', '_plus_').replace('-', '_minus_').replace('/','_')
        print >> outf, 'class test_%s(unittest.TestCase):' % tname
        print >> outf, '    def test(self):'
        zd_out, zd_in = popen2.popen2('%s -v %s' % (zdump, zone))
        zd_in.close()
        lines = zd_out.readlines()
        prev_dt = None
        prev_is_dst = False
        for idx in range(0, len(lines)):
            line = lines[idx]
            m = re.match(
                '^([^\s]+)\s+(.+\sUTC) \s+=\s+ (.+)\s([^\s]+) \s+isdst=(0|1)$',
                line, re.X
                )
            if m:
                zone, utc_string, local_string, tzname, is_dst = m.groups()
            else:
                raise RuntimeError, 'Dud line %r' % (line,)

            def to_datetime(s):
                bits = s.split()
                tz_abbr = bits[-1]
                s = ' '.join(bits[:-1])
                try:
                    return datetime(*strptime(s, '%a %b %d %H:%M:%S %Y')[:6])
                except:
                    print 's==%s'%repr(s)
                    raise

            local_dt = to_datetime('%s %s' % (local_string, tzname))
            utc_dt = to_datetime(utc_string)

            # Urgh - utcoffset() and dst() have to be rounded to the nearest
            # minute, so we need to break our tests to match this limitation
            real_offset = local_dt - utc_dt
            secs = real_offset.seconds + real_offset.days*86400
            fake_offset = timedelta(seconds=int((secs+30)/60)*60)
            local_dt = utc_dt + fake_offset

            # If the naive time on the previous line is greater than on this
            # line, and we arn't seeing an end-of-dst transition, then
            # we can't do our local->utc test since we are in an ambiguous
            # time period (ie. we have wound back the clock but don't have
            # differing is_dst flags to resolve the ambiguity)
            if prev_dt is not None and prev_dt > local_dt and \
                    bool(prev_is_dst) == bool(is_dst):
                skip_local_test = True
            else:
                skip_local_test = False
            prev_is_dst = is_dst
            prev_dt = local_dt

            local_string = '%s %s' % (
                    local_dt.strftime('%a %b %d %H:%M:%S %Y'), tzname
                    )
            utc_string = '%s UTC' % utc_dt.strftime('%a %b %d %H:%M:%S %Y')


            tmp1 = line.split()[0]
            tmp2 = line[len(tmp1):].strip()

            print >> outf, '# %s\n# %s\n' % (tmp1, tmp2)
            print >> outf, '        self.failUnlessEqual('
            print >> outf, '            aszone(%r, %r),' % (utc_string, zone)
            print >> outf, '                   %r,' % (local_string,)
            print >> outf, '            )\n'
            if not skip_local_test:
                print >> outf, '        self.failUnlessEqual('
                print >> outf, '            asutc(%r, %r, is_dst=%d),' % (
                        local_string, zone, int(is_dst)
                        )
                print >> outf, '                  %r,' % (utc_string,)
                print >> outf, '            )\n'

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

def asutc(loc_string, zone, is_dst):
    loc_tz = timezone(zone)
    loc_string = ' '.join(loc_string.split()[:-1]) # Remove timezone
    loc_t = strptime(loc_string, '%a %b %d %H:%M:%S %Y')[:6]
    loc_datetime = loc_tz.normalize(datetime(*loc_t), is_dst=is_dst)
    utc_datetime = loc_datetime.astimezone(utc_tz)
    return '%s' % (utc_datetime.strftime('%a %b %d %H:%M:%S %Y %Z'))

if __name__ == '__main__':
    unittest.main()

"""

if __name__ == '__main__':
    try:
        gen_tzinfo.target = sys.argv[1:]
    except IndexError:
        gen_tzinfo.target = None
    main()

# vim: set filetype=python ts=4 sw=4 et

