#!/usr/bin/python2.4

import os.path, sys
sys.path.insert(0, os.path.join('build', 'dist'))

from datetime import datetime, timedelta
import new
import re
from time import strptime
import unittest
import pytz


class ZdumpTestCase(unittest.TestCase):
    def utc_to_local_check(self, zone, utc_dt, loc_dt, loc_tzname, is_dst):
        loc_tz = pytz.timezone(zone)
        self.failUnlessEqual(
            utc_dt.astimezone(loc_tz).replace(tzinfo=None),
            loc_dt.replace(tzinfo=None))

    def local_to_utc_check(self, zone, utc_dt, loc_dt, loc_tzname, is_dst):
        loc_tz = pytz.timezone(zone)
        self.failUnlessEqual(
            loc_dt.astimezone(pytz.utc).replace(tzinfo=None),
            utc_dt.replace(tzinfo=None))


def test_suite():
    testcases = []
    raw_data = open(
        os.path.join(os.path.dirname(__file__), 'zdump.out'), 'r').readlines()
    raw_data.reverse() # Keep tests running in alphabetical order
    last_zone = None
    test_class = None
    for line in raw_data:
        m = re.match(
        r'^([^\s]+) \s+ (.+) \s UTC \s+ = \s+ (.+) \s ([^\s]+) \s+ '
            r'isdst=(0|1)$',
            line, re.X
            )
        if m:
            zone, utc_string, loc_string, tzname, is_dst = m.groups()
        else:
            raise RuntimeError, 'Dud line %r' % (line,)

        if zone != last_zone:
            classname = zone.replace(
                    '+', '_plus_').replace('-', '_minus_').replace('/','_')
            test_class = type(classname, (ZdumpTestCase,), {})
            testcases.append(test_class)
            last_zone = zone
            prev_loc_dt = None
            prev_is_dst = False

        utc_dt = datetime(
            *strptime(utc_string, '%a %b %d %H:%M:%S %Y')[:6])
        loc_dt = datetime(
            *strptime(loc_string, '%a %b %d %H:%M:%S %Y')[:6])

        # Urgh - utcoffset() and dst() have to be rounded to the nearest
        # minute, so we need to break our tests to match this limitation
        real_offset = loc_dt - utc_dt
        secs = real_offset.seconds + real_offset.days*86400
        fake_offset = timedelta(seconds=int((secs+30)/60)*60)
        loc_dt = utc_dt + fake_offset

        # If the naive time on the previous line is greater than on this
        # line, and we arn't seeing an end-of-dst transition, then
        # we can't do our local->utc test since we are in an ambiguous
        # time period (ie. we have wound back the clock but don't have
        # differing is_dst flags to resolve the ambiguity)
        skip_local = (
            prev_loc_dt is not None and prev_loc_dt > loc_dt and
            bool(prev_is_dst) == bool(is_dst))
        prev_loc_dt = loc_dt
        prev_is_dst = is_dst

        loc_tz = pytz.timezone(zone)
        loc_dt = loc_tz.localize(loc_dt, is_dst)

        utc_dt = pytz.utc.localize(utc_dt)

        test_name = 'test_utc_to_local_%04d_%02d_%02d_%02d_%02d_%02d' % (
            utc_dt.year, utc_dt.month, utc_dt.day,
            utc_dt.hour, utc_dt.minute, utc_dt.second)
        def test_utc_to_local(self):
            self.utc_to_local_check(zone, utc_dt, loc_dt, tzname, is_dst)
        test_utc_to_local.__name__ = test_name
        #test_utc_to_local.__doc__ = line
        setattr(test_class, test_name, test_utc_to_local)

        if not skip_local:
            test_name = 'test_local_to_utc_%04d_%02d_%02d_%02d_%02d_%02d' % (
                utc_dt.year, utc_dt.month, utc_dt.day,
                utc_dt.hour, utc_dt.minute, utc_dt.second)
            def test_local_to_utc(self):
                self.utc_to_local_check(zone, utc_dt, loc_dt, tzname, is_dst)
            test_local_to_utc.__name__ = test_name
            #test_local_to_utc.__doc__ = line
            setattr(test_class, test_name, test_local_to_utc)


    suite = unittest.TestSuite()
    while testcases:
        suite.addTest(unittest.makeSuite(testcases.pop()))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
