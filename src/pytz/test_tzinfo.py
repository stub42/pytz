#!/usr/bin/env python
# -*- coding: ascii -*-
'''
$Id: test_tzinfo.py,v 1.4 2004/06/06 10:07:00 zenzen Exp $
'''

__rcs_id__  = '$Id: test_tzinfo.py,v 1.4 2004/06/06 10:07:00 zenzen Exp $'
__version__ = '$Revision: 1.4 $'[11:-2]

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

    def test_arithmetic(self):
        utc_dt = self.transition_time

        for days in range(-420, 720, 20):
            delta = timedelta(days=days)

            # Make sure we can get back where we started
            dt = utc_dt.astimezone(self.tzinfo)
            dt2 = dt + delta
            dt2 = dt2 - delta
            self.failUnlessEqual(dt, dt2)

            # Make sure arithmetic crossing DST boundaries ends
            # up in the correct timezone after normalization
            fmt = '%Y-%m-%d %H:%M:%S %Z (%z)'
            self.failUnlessEqual(
                    (utc_dt + delta).astimezone(self.tzinfo).strftime(fmt),
                    self.tzinfo.normalize(dt + delta).strftime(fmt),
                    #(dt + delta).strftime(fmt),
                    'Incorrect result for delta==%d days.  Wanted %r. Got %r'%(
                        days,
                        (utc_dt + delta).astimezone(self.tzinfo).strftime(fmt),
                        self.tzinfo.normalize(dt + delta).strftime(fmt),
                        #(dt + delta).strftime(fmt),
                        )
                    )

    def _test_all(self, utc_dt, wanted):
        self._test_utcoffset(utc_dt, wanted)
        self._test_tzname(utc_dt, wanted)
        self._test_dst(utc_dt, wanted)

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
    def test_arithmetic(self):
        # Reference implementation cannot handle this
        pass


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

    def test_arithmetic(self):
        # Reference implementation cannot handle this
        pass


if __name__ == '__main__':
    unittest.main()

# vim: set filetype=python ts=4 sw=4 et

