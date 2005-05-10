#!/usr/bin/env python
# -*- coding: ascii -*-
'''
$Id: test_tzinfo.py,v 1.2 2004/06/05 11:34:44 zenzen Exp $
'''

__rcs_id__  = '$Id: test_tzinfo.py,v 1.2 2004/06/05 11:34:44 zenzen Exp $'
__version__ = '$Revision: 1.2 $'[11:-2]

import sys, os
sys.path.insert(0, os.pardir)

import unittest
from datetime import datetime, tzinfo, timedelta
import pytz, reference

NOTIME = timedelta(0)

UTC = reference.utc

class BasicTest(unittest.TestCase):
    def testUTC(self):
        UTC = pytz.timezone('UTC')
        now = datetime.now(tz=UTC)
        self.failUnless(now.utcoffset() == NOTIME)
        self.failUnless(now.dst() == NOTIME)
        self.failUnless(now.timetuple() == now.utctimetuple())

    def testReferenceUTC(self):
        UTC = reference.utc
        now = datetime.now(tz=UTC)
        self.failUnless(now.utcoffset() == NOTIME)
        self.failUnless(now.dst() == NOTIME)
        self.failUnless(now.timetuple() == now.utctimetuple())


class USEasternDSTStartTestCase(unittest.TestCase):
    tzinfo = pytz.timezone('US/Eastern')

    # 24 hours before DST changeover
    transition_time = datetime(2002, 4, 7, 7, 0, 0, tzinfo=UTC)

    # before transition
    before = {
        'tzname': 'EST',
        'utcoffset': timedelta(hours = -5),
        'dst': timedelta(hours = 0),
        }

    # after transition
    after = {
        'tzname': 'EDT',
        'utcoffset': timedelta(hours = -4),
        'dst': timedelta(hours = 1),
        }

    def _test_tzname(self, utc_dt, wanted):
        dt = utc_dt.astimezone(self.tzinfo)
        self.failUnlessEqual(dt.tzname(),wanted['tzname'],
            'Expected %s as tzname for %s. Got %s' % (
                wanted['tzname'],str(utc_dt),dt.tzname()
                )
            )

    def _test_utcoffset(self, utc_dt, wanted):
        utcoffset = wanted['utcoffset']
        dt = utc_dt.astimezone(self.tzinfo)
        self.failUnlessEqual(
                dt.utcoffset(),utcoffset,
                'Expected %s as utcoffset for %s. Got %s' % (
                    utcoffset,utc_dt,dt.utcoffset()
                    )
                )
        return
        dt_wanted = utc_dt.replace(tzinfo=None) + utcoffset
        dt_got = dt.replace(tzinfo=None)
        self.failUnlessEqual(
                dt_wanted,
                dt_got,
                'Got %s. Wanted %s' % (str(dt_got),str(dt_wanted))
                )

    def _test_dst(self, utc_dt, wanted):
        dst = wanted['dst']
        dt = utc_dt.astimezone(self.tzinfo)
        self.failUnlessEqual(dt.dst(),dst,
            'Expected %s as dst for %s. Got %s' % (
                dst,utc_dt,dt.dst()
                )
            )

    def _test_arithmetic(self, utc_dt):
        for days in range(-720, 720, 20):
            dt = utc_dt.astimezone(self.tzinfo)
            dt2 = dt + timedelta(days=days)
            dt2 = dt2 - timedelta(days=days)
            self.failUnlessEqual(dt, dt2)
            self.failUnlessEqual(str(dt), str(dt2))

    def _test_roundtrip(self, utc_dt):
        self.failUnlessEqual(
                utc_dt.astimezone(self.tzinfo).astimezone(UTC),
                utc_dt,
                )
        self.failUnlessEqual(
                str(utc_dt.astimezone(self.tzinfo).astimezone(UTC)),
                str(utc_dt),
                )

    def _test_all(self, utc_dt, wanted):
        self._test_utcoffset(utc_dt, wanted)
        self._test_tzname(utc_dt, wanted)
        self._test_dst(utc_dt, wanted)
        self._test_arithmetic(utc_dt)

    def testDayBefore(self):
        self._test_all(
                self.transition_time - timedelta(days=1), self.before
                )

    def testTwoHoursBefore(self):
        self._test_all(
                self.transition_time - timedelta(hours=2), self.before
                )

    def testHourBefore(self):
        self._test_all(
                self.transition_time - timedelta(hours=1), self.before
                )

    def testInstantBefore(self):
        self._test_all(
                self.transition_time - timedelta(seconds=1), self.before
                )

    def testTransition(self):
        self._test_all(
                self.transition_time, self.after
                )

    def testInstantAfter(self):
        self._test_all(
                self.transition_time + timedelta(seconds=1), self.after
                )

    def testHourAfter(self):
        self._test_all(
                self.transition_time + timedelta(hours=1), self.after
                )

    def testTwoHoursAfter(self):
        self._test_all(
                self.transition_time + timedelta(hours=1), self.after
                )

    def testDayAfter(self):
        self._test_all(
                self.transition_time + timedelta(days=1), self.after
                )


class USEasternDSTEndTestCase(USEasternDSTStartTestCase):
    tzinfo = pytz.timezone('US/Eastern')
    transition_time = datetime(2002, 10, 27, 6, 0, 0, tzinfo=UTC)
    before = {
        'tzname': 'EDT',
        'utcoffset': timedelta(hours = -4),
        'dst': timedelta(hours = 1),
        }
    after = {
        'tzname': 'EST',
        'utcoffset': timedelta(hours = -5),
        'dst': timedelta(hours = 0),
        }


class ReferenceUSEasternDSTStartTestCase(USEasternDSTStartTestCase):
    tzinfo = reference.Eastern


class ReferenceUSEasternDSTEndTestCase(USEasternDSTEndTestCase):
    tzinfo = reference.Eastern

    def testHourBefore(self):
        # Python's datetime library has a bug, where the hour before
        # a daylight savings transition is one hour out. For example,
        # at the end of US/Eastern daylight savings time, 01:00 EST
        # occurs twice (once at 05:00 UTC and once at 06:00 UTC),
        # whereas the first should actually be 01:00 EDT.
        # Note that this bug is by design - by accepting this ambiguity
        # for one hour one hour per year, an is_dst flag on datetime.time
        # became unnecessary.
        self._test_all(
                self.transition_time - timedelta(hours=1), self.after
                )

    def testInstantBefore(self):
        self._test_all(
                self.transition_time - timedelta(seconds=1), self.after
                )

if __name__ == '__main__':
    unittest.main()

# vim: set filetype=python ts=4 sw=4 et

