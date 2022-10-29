#!/usr/bin/python2.7

import os.path
import sys
sys.path.insert(0, os.path.join('build', 'dist'))

from datetime import datetime, timedelta
import re
from time import strptime
import unittest
import pytz


class ZdumpTestCase(unittest.TestCase):
    def utc_to_local_check(self, zone, utc_dt, loc_dt, loc_tzname, is_dst):
        loc_tz = pytz.timezone(zone)
        self.assertEqual(
            utc_dt.astimezone(loc_tz).replace(tzinfo=None),
            loc_dt.replace(tzinfo=None)
        )

    def local_to_utc_check(self, zone, utc_dt, loc_dt, loc_tzname, is_dst):
        self.assertEqual(
            loc_dt.astimezone(pytz.utc).replace(tzinfo=None),
            utc_dt.replace(tzinfo=None)
        )


def test_suite():
    testcases = []
    raw_data = open(
        os.path.join(os.path.dirname(__file__), 'zdump.out'), 'r').readlines()
    last_zone = None
    test_class = None
    zdump_line_re = re.compile(r'''(?x)
        ^([^\s]+) \s+ (.+) \s UT \s+ = \s+ (.+) \s ([^\s]+) \s+
                               isdst=(0|1) \s+ gmtoff=[\-\d]+ \s*$
        ''')
    for i in range(0, len(raw_data)):
        line = raw_data[i]
        m = zdump_line_re.search(line)
        if m is None:
            raise RuntimeError('Dud line %r' % (line,))
        zone, utc_string, loc_string, tzname, is_dst = m.groups()
        is_dst = bool(int(is_dst))

        if zone != last_zone:
            classname = zone.replace(
                '+', '_plus_').replace('-', '_minus_').replace('/', '_')
            test_class = type(classname, (ZdumpTestCase,), {})
            testcases.append(test_class)
            last_zone = zone
            skip_next_local = False

        utc_dt = datetime(
            *strptime(utc_string, '%a %b %d %H:%M:%S %Y')[:6])
        loc_dt = datetime(
            *strptime(loc_string, '%a %b %d %H:%M:%S %Y')[:6])

        def round_dt(loc_dt, utc_dt):
            # Urgh - utcoffset() and dst() have to be rounded to the nearest
            # minute, so we need to break our tests to match this limitation
            real_offset = loc_dt - utc_dt
            secs = real_offset.seconds + real_offset.days * 86400
            fake_offset = timedelta(seconds=int((secs + 30) // 60) * 60)
            return utc_dt + fake_offset

        loc_dt = round_dt(loc_dt, utc_dt)

        # If the naive time on the next line is less than on this
        # line, and we aren't seeing an end-of-dst transition, then
        # we can't do our local->utc tests for either this nor the
        # next line since we are in an ambiguous time period (ie.
        # we have wound back the clock but don't have differing
        # is_dst flags to resolve the ambiguity)
        skip_local = skip_next_local
        skip_next_local = False
        try:
            m = zdump_line_re.match(raw_data[i + 1])
        except IndexError:
            m = None
        if m is not None:
            (next_zone, next_utc_string, next_loc_string,
                next_tzname, next_is_dst) = m.groups()
            next_is_dst = bool(int(next_is_dst))
            if next_zone == zone and next_is_dst == is_dst:
                next_utc_dt = datetime(
                    *strptime(next_utc_string, '%a %b %d %H:%M:%S %Y')[:6])
                next_loc_dt = round_dt(
                    datetime(*strptime(
                        next_loc_string, '%a %b %d %H:%M:%S %Y')[:6]),
                    next_utc_dt)
                if next_loc_dt <= loc_dt:
                    skip_local = True
                    skip_next_local = True

        loc_tz = pytz.timezone(zone)
        loc_dt = loc_tz.localize(loc_dt, is_dst)

        utc_dt = pytz.utc.localize(utc_dt)

        test_name = 'test_utc_to_local_%04d_%02d_%02d_%02d_%02d_%02d' % (
            utc_dt.year, utc_dt.month, utc_dt.day,
            utc_dt.hour, utc_dt.minute, utc_dt.second)

        def test_utc_to_local(
                self, zone=zone, utc_dt=utc_dt, loc_dt=loc_dt,
                tzname=tzname, is_dst=is_dst):
            self.utc_to_local_check(zone, utc_dt, loc_dt, tzname, is_dst)
        test_utc_to_local.__name__ = test_name
        setattr(test_class, test_name, test_utc_to_local)

        if not skip_local:
            test_name = 'test_local_to_utc_%04d_%02d_%02d_%02d_%02d_%02d' % (
                loc_dt.year, loc_dt.month, loc_dt.day,
                loc_dt.hour, loc_dt.minute, loc_dt.second)
            if is_dst:
                test_name += '_dst'
            else:
                test_name += '_nodst'

            def test_local_to_utc(
                    self, zone=zone, utc_dt=utc_dt, loc_dt=loc_dt,
                    tzname=tzname, is_dst=is_dst):
                self.local_to_utc_check(zone, utc_dt, loc_dt, tzname, is_dst)
            test_local_to_utc.__name__ = test_name
            setattr(test_class, test_name, test_local_to_utc)

    classname = zone.replace(
        '+', '_plus_').replace('-', '_minus_').replace('/', '_')
    test_class = type(classname, (ZdumpTestCase,), {})
    testcases.append(test_class)

    suite = unittest.TestSuite()
    while testcases:
        suite.addTest(unittest.makeSuite(testcases.pop()))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
