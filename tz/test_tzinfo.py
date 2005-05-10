#!/usr/bin/env python
# -*- coding: ascii -*-
'''
$Id: test_tzinfo.py,v 1.1 2004/05/31 00:31:19 zenzen Exp $
'''

__rcs_id__  = '$Id: test_tzinfo.py,v 1.1 2004/05/31 00:31:19 zenzen Exp $'
__version__ = '$Revision: 1.1 $'[11:-2]

import sys, os
sys.path.insert(0, os.pardir)

import unittest
from datetime import datetime, tzinfo, timedelta
import tz, reference

NOTIME = timedelta(0)

UTC = reference.utc

class BasicTest(unittest.TestCase):
    def testUTC(self):
        UTC = tz.timezone('UTC')
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
    tzinfo = tz.timezone('US/Eastern')

    # 24 hours before DST kicks in
    transition_time = datetime(2002, 4, 7, 7, 0, 0, tzinfo=UTC)

    # before transition
    before_tzname = 'EST'
    before_utcoffset = timedelta(hours = -5)
    before_dst = timedelta(hours = 0)

    # after transition
    after_tzname = 'EDT'
    after_utcoffset = timedelta(hours = -4)
    after_dst = timedelta(hours = 1)

    def _test_tzname(self,utc_dt,tzname):
        dt = utc_dt.astimezone(self.tzinfo)
        self.failUnlessEqual(dt.tzname(),tzname,
            'Expected %s as tzname for %s. Got %s' % (
                tzname,str(utc_dt),dt.tzname()
                )
            )

    def _test_utcoffset(self,utc_dt,utcoffset):
        dt = utc_dt.astimezone(self.tzinfo)
        dt_wanted = utc_dt.replace(tzinfo=None) + utcoffset
        dt_got = dt.replace(tzinfo=None)
        self.failUnlessEqual(
                dt_wanted,
                dt_got,
                'Wanted %s. Got %s' % (str(dt_wanted),str(dt_got))
                )
        self.failUnlessEqual(dt.utcoffset(),utcoffset,
            'Expected %s as utcoffset for %s. Got %s' % (
                utcoffset,utc_dt,dt.utcoffset()
                )
            )

    def _test_dst(self,utc_dt,dst):
        dt = utc_dt.astimezone(self.tzinfo)
        self.failUnlessEqual(dt.dst(),dst,
            'Expected %s as dst for %s. Got %s' % (
                dst,utc_dt,dt.dst()
                )
            )

    def testLeadup(self):
        for i in range(-320, 0):
            delta = timedelta(minutes=i)
            self._test_tzname(self.transition_time + delta, self.before_tzname)
            self._test_utcoffset(
                    self.transition_time + delta, self.before_utcoffset
                    )
            self._test_dst(self.transition_time + delta, self.before_dst)

    def testDayBefore(self):
        delta = timedelta(days=-1)
        self._test_tzname(self.transition_time + delta, self.before_tzname)
        self._test_utcoffset(self.transition_time+delta, self.before_utcoffset)
        self._test_dst(self.transition_time+delta, self.before_dst)

    def testInstantBefore(self):
        delta = timedelta(seconds=-1)
        self._test_tzname(self.transition_time + delta, self.before_tzname)
        self._test_utcoffset(self.transition_time+delta, self.before_utcoffset)
        self._test_dst(self.transition_time + delta, self.before_dst)

    def testTransition(self):
        delta = timedelta(0)
        self._test_tzname(self.transition_time + delta, self.after_tzname)
        self._test_utcoffset(self.transition_time+delta, self.after_utcoffset)
        self._test_dst(self.transition_time + delta, self.after_dst)

    def testInstantAfter(self):
        delta = timedelta(seconds=1)
        self._test_tzname(self.transition_time + delta, self.after_tzname)
        self._test_utcoffset(self.transition_time+delta, self.after_utcoffset)
        self._test_dst(self.transition_time + delta, self.after_dst)

    def testFollowthrough(self):
        for i in range(321, 1, -1):
            delta = timedelta(minutes=i)
            self._test_tzname(self.transition_time + delta, self.after_tzname)
            self._test_utcoffset(
                    self.transition_time + delta, self.after_utcoffset
                    )
            self._test_dst(self.transition_time + delta, self.after_dst)

    def testDayAfter(self):
        delta = timedelta(days=1)
        self._test_tzname(self.transition_time + delta, self.after_tzname)
        self._test_utcoffset(self.transition_time + delta, self.after_utcoffset)
        self._test_dst(self.transition_time + delta, self.after_dst)


class USEasternDSTEndTestCase(USEasternDSTStartTestCase):
    tzinfo = tz.timezone('US/Eastern')
    transition_time = datetime(2002, 10, 27, 6, 0, 0, tzinfo=UTC)
    before_tzname = 'EDT'
    before_utcoffset = timedelta(hours = -4)
    before_dst = timedelta(hours = 1)
    after_tzname = 'EST'
    after_utcoffset = timedelta(hours = -5)
    after_dst = timedelta(hours = 0)


class ReferenceUSEasternDSTStartTestCase(USEasternDSTStartTestCase):
    tzinfo = reference.Eastern


class ReferenceUSEasternDSTEndTestCase(USEasternDSTEndTestCase):
    tzinfo = reference.Eastern

if __name__ == '__main__':
    unittest.main()

# vim: set filetype=python ts=4 sw=4 et

