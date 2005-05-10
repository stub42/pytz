#!/usr/bin/env python
# -*- coding: ascii -*-
'''
$Id: test_tzinfo.py,v 1.5 2004/07/22 01:44:31 zenzen Exp $
'''

__rcs_id__  = '$Id: test_tzinfo.py,v 1.5 2004/07/22 01:44:31 zenzen Exp $'
__version__ = '$Revision: 1.5 $'[11:-2]

import sys, os
sys.path.insert(0, os.pardir)

import unittest, doctest
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

class USEasternEPTStartTestCase(USEasternDSTStartTestCase):
    transition_time = datetime(1945, 8, 14, 23, 0, 0, tzinfo=UTC)
    before = {
        'tzname': 'EWT',
        'utcoffset': timedelta(hours = -4),
        'dst': timedelta(hours = 1),
        }
    after = {
        'tzname': 'EPT',
        'utcoffset': timedelta(hours = -4),
        'dst': timedelta(hours = 1),
        }

class USEasternEPTEndTestCase(USEasternDSTStartTestCase):
    transition_time = datetime(1945, 9, 30, 6, 0, 0, tzinfo=UTC)
    before = {
        'tzname': 'EPT',
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


class LocalTestCase(unittest.TestCase):
    def testNormalizeZone(self):
        loc_tz = pytz.timezone('Europe/Amsterdam')

        loc_time = loc_tz.normalize(datetime(1930, 5, 10, 0, 0, 0))
        # Actually +00:19:32, but Python datetime rounds this
        self.failUnlessEqual(loc_time.strftime('%Z%z'), 'AMT+0020')

        loc_time = loc_tz.normalize(datetime(1930, 5, 20, 0, 0, 0))
        # Actually +00:19:32, but Python datetime rounds this
        self.failUnlessEqual(loc_time.strftime('%Z%z'), 'NST+0120')

        loc_time = loc_tz.normalize(datetime(1940, 5, 10, 0, 0, 0))
        self.failUnlessEqual(loc_time.strftime('%Z%z'), 'NET+0020')

        loc_time = loc_tz.normalize(datetime(1940, 5, 20, 0, 0, 0))
        self.failUnlessEqual(loc_time.strftime('%Z%z'), 'CEST+0200')

        loc_time = loc_tz.normalize(datetime(2004, 2, 1, 0, 0, 0))
        self.failUnlessEqual(loc_time.strftime('%Z%z'), 'CET+0100')

        loc_time = loc_tz.normalize(datetime(2004, 4, 1, 0, 0, 0))
        self.failUnlessEqual(loc_time.strftime('%Z%z'), 'CEST+0200')

        # Weird changes - war time and peace time both is_dst==True
        loc_tz = pytz.timezone('US/Eastern')
        loc_time = loc_tz.normalize(datetime(1942, 2, 9, 3, 0, 0))
        self.failUnlessEqual(loc_time.strftime('%Z%z'), 'EWT-0400')

        loc_time = loc_tz.normalize(datetime(1945, 8, 14, 19, 0, 0))
        self.failUnlessEqual(loc_time.strftime('%Z%z'), 'EPT-0400')

        loc_time = loc_tz.normalize(datetime(1945, 9, 30, 1, 0, 0), is_dst=1)
        self.failUnlessEqual(loc_time.strftime('%Z%z'), 'EPT-0400')

        loc_time = loc_tz.normalize(datetime(1945, 9, 30, 1, 0, 0), is_dst=0)
        self.failUnlessEqual(loc_time.strftime('%Z%z'), 'EST-0500')

    def testNormalize(self):
        tz = pytz.timezone('US/Eastern')
        dt = datetime(2004, 4, 4, 7, 0, 0, tzinfo=UTC).astimezone(tz)
        dt2 = dt - timedelta(minutes=10)
        self.failUnlessEqual(
                dt2.strftime('%Y-%m-%d %H:%M:%S %Z%z'),
                '2004-04-04 02:50:00 EDT-0400'
                )

        dt2 = tz.normalize(dt2)
        self.failUnlessEqual(
                dt2.strftime('%Y-%m-%d %H:%M:%S %Z%z'),
                '2004-04-04 01:50:00 EST-0500'
                )


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite('pytz'))
    suite.addTest(doctest.DocTestSuite('pytz.tzinfo'))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(
        __import__('__main__')
        ))
    return suite

if __name__ == '__main__':
    suite = test_suite()
    if '-v' in sys.argv:
        runner = unittest.TextTestRunner(verbosity=2)
    else:
        runner = unittest.TextTestRunner()
    runner.run(suite)

# vim: set filetype=python ts=4 sw=4 et

