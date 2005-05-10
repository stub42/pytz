'''
$Id: test_tzinfo.py,v 1.7 2004/05/31 00:27:39 zenzen Exp $
'''
import sys, os
sys.path.insert(0, os.curdir)

import re
import unittest
import pickle
import popen2
import os.path
import datetime
from time import strptime

import reference # Tim Peter's tzinfo examples
import tz

from gen_tzinfo import allzones

utc_tzinfo = reference.utc

class UTCTestCase(unittest.TestCase):
    def testTz(self):
        # Test UTC as returned from the library
        UTC = tz.timezone('UTC')
        now = datetime.datetime.now(tz=UTC)
        self.failUnless(now.utcoffset() == datetime.timedelta(0))
        self.failUnless(now.dst() == datetime.timedelta(0))
        self.failUnless(now.timetuple() == now.utctimetuple())

    def testReference(self):
        # Test UTC from reference, which these tests use
        now = datetime.datetime.now(tz=utc_tzinfo)
        self.failUnless(now.utcoffset() == datetime.timedelta(0))
        self.failUnless(now.dst() == datetime.timedelta(0))
        self.failUnless(now.timetuple() == now.utctimetuple())


class USEasternDSTStartTestCase(unittest.TestCase):
    tzinfo = tz.timezone('US/Eastern')

    # 24 hours before DST kicks in
    dayBefore = datetime.datetime(2002, 4, 6, 7, 0, 0, tzinfo=utc_tzinfo)

    # before transition
    before_tzname = 'EST'
    before_utcoffset = datetime.timedelta(hours = -5)
    before_dst = datetime.timedelta(hours = 0)

    # after transition
    after_tzname = 'EDT'
    after_utcoffset = datetime.timedelta(hours = -4)
    after_dst = datetime.timedelta(hours = 1)

    def _test_tzname(self,utc_dt,tzname):
        dt = utc_dt.astimezone(self.tzinfo)
        self.failUnlessEqual(dt.tzname(),tzname,
            'Expected %s as tzname for %s. Got %s' % (
                tzname,str(utc_dt),dt.tzname()
                )
            )

    def _test_utcoffset(self,utc_dt,utcoffset):
        dt = utc_dt.astimezone(self.tzinfo)
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

    def testDayBefore(self):
        self._test_tzname(self.dayBefore, self.before_tzname)
        self._test_utcoffset(self.dayBefore, self.before_utcoffset)
        self._test_dst(self.dayBefore, self.before_dst)

    def testInstantBefore(self):
        delta = datetime.timedelta(days=1, seconds=-1)
        self._test_tzname(self.dayBefore + delta, self.before_tzname)
        self._test_utcoffset(self.dayBefore + delta, self.before_utcoffset)
        self._test_dst(self.dayBefore + delta, self.before_dst)

    def testInstantAfter(self):
        delta = datetime.timedelta(days=1)
        self._test_tzname(self.dayBefore + delta, self.after_tzname)
        self._test_utcoffset(self.dayBefore + delta, self.after_utcoffset)
        self._test_dst(self.dayBefore + delta, self.after_dst)

    def testDayAfter(self):
        delta = datetime.timedelta(days=2)
        self._test_tzname(self.dayBefore + delta, self.after_tzname)
        self._test_utcoffset(self.dayBefore + delta, self.after_utcoffset)
        self._test_dst(self.dayBefore + delta, self.after_dst)

    '''
    def test_leadup(self):
        # Test every second for 15 minutes before
        for i in xrange(0,15*60):
            delta = (
                    datetime.timedelta(hours=23,minutes=45) +
                    datetime.timedelta(seconds=i)
                    )
            assert delta < datetime.timedelta(hours=24)
            self._test_tzname(self.dayBefore + delta, self.before_tzname)
            self._test_utcoffset(self.dayBefore + delta, self.before_utcoffset)
            self._test_dst(self.dayBefore + delta, self.before_dst)

    def test_followthrough(self):
        # Test every second for 15 minutes after
        for i in xrange(1,15*60):
            delta = datetime.timedelta(hours=24) + datetime.timedelta(seconds=i)
            self._test_tzname(self.dayBefore + delta, self.after_tzname)
            self._test_utcoffset(self.dayBefore + delta, self.after_utcoffset)
            self._test_dst(self.dayBefore + delta, self.after_dst)
    '''

class USEasternDSTEndTestCase(USEasternDSTStartTestCase):
    tzinfo = tz.timezone('US/Eastern')
    dayBefore = datetime.datetime(2002, 10, 26, 6, 0, 0, tzinfo=utc_tzinfo)
    before_tzname = 'EDT'
    before_utcoffset = datetime.timedelta(hours = -4)
    before_dst = datetime.timedelta(hours = 1)
    after_tzname = 'EST'
    after_utcoffset = datetime.timedelta(hours = -5)
    after_dst = datetime.timedelta(hours = 0)

#class ReferenceEasternDSTStartTestCase(USEasternDSTStartTestCase):
#    tzinfo = reference.Eastern

#class ReferenceEasternDSTEndTestCase(USEasternDSTEndTestCase):
#    tzinfo = reference.Eastern

transitions_cache = {}

class ZDumpTransitionTimesTestCase(unittest.TestCase):
    zdump = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'build','etc','zdump'
            ))

    def transitions(self,zone):
        try:
            for t in transitions_cache[zone]:
                yield t
        except KeyError:
            transitions_cache[zone] = []
            (zd_out,zd_in) = popen2.popen2('%s -v %s' % (self.zdump,zone))
            zd_in.close()
            tzinfo = tz.timezone(zone)
            lines = zd_out.readlines()
            lines = lines[15:-15]
            for line in lines:
                fmt = '^([^\s]+) \s+(.*)\s UTC \s=\s(.*) \s(\w+)\s isdst=(0|1)$'
                m = re.match(fmt, line, re.X)
                if m:
                    zone2, utc_t, loc_t, abbr, is_dst = m.groups()
                else:
                    raise RuntimeError, 'Dud line %r' % (line,)

                assert zone == zone2

                datefmt = '%a %b %d %H:%M:%S %Y'
                utc_t = strptime(utc_t,datefmt)
                loc_t = strptime(loc_t,datefmt)
                if utc_t[0] < 2000:
                    continue

                t = tzinfo,utc_t,loc_t,abbr,bool(int(is_dst))
                transitions_cache[zone].append(t)
                yield t

    def _test_matchzdump(self,zone):
        for tz,utc_t,loc_t,tzname,is_dst in self.transitions(zone):
            args = list(utc_t[:6]) + [0,utc_tzinfo]
            utc = datetime.datetime(*args)
            loc = utc.astimezone(tz)

            self.failUnlessEqual(tzname,loc.tzname(),
                'Incorrect tzname for %s. Wanted %s. Got %s' % (
                    utc,tzname,loc.tzname()
                    )
                )

            self.failUnlessEqual(is_dst,loc.dst() != datetime.timedelta(0),
                'Incorrect is_dst for %s. Wanted %s' % (loc,is_dst)
                )

            # Convert loc to naieve time
            nloc = loc.replace(tzinfo=None)
            nwanted = datetime.datetime(*loc_t[:6])

            self.failUnlessEqual(nwanted,nloc,
                'Got %s from %s using tzinfo %r. Wanted %s)' % (
                    loc,utc,tz,nwanted
                    )
                )

    """
    def test_EasternReference(self):
        for tz,utc_t,loc_t,tzname,is_dst in self.transitions('US/Eastern'):
            if utc_t[0] not in range(2000,2004):
                continue
            dt = datetime.datetime(*(utc_t[:6]))
            dt = dt.replace(tzinfo=utc_tzinfo)

            as_ref = dt.astimezone(reference.Eastern)
            as_tz = dt.astimezone(tz)

            self.failUnlessEqual(as_ref, as_tz,
                'Expected %s, got %s from %s' % (as_ref, as_tz, dt)
                )

            self.failUnlessEqual(as_ref.tzname(),as_tz.tzname(),
                'Expected %s, got %s from %s' % (
                    as_ref.tzname(), as_tz.tzname(), dt
                    )
                )

            self.failUnlessEqual(as_ref.utcoffset(),as_tz.utcoffset(),
                'Expected %s, got %s from %s' % (
                    as_ref.utcoffset(), as_tz.utcoffset(), dt
                    )
                )

            self.failUnlessEqual(as_ref.dst(),as_tz.dst(),
                'Expected %s, got %s from %s' % (
                    as_ref.dst(), as_tz.dst(), dt
                    )
                )
    """

def fillZDumpTest(cls):
    ''' Add tests to ZDump '''
    zones = allzones()

    #zones = []
    #zoneinfo = os.path.abspath(os.path.join(
    #    os.path.dirname(__file__), 'build', 'etc', 'zoneinfo'
    #    ))
    #for dirpath, dirnames, filenames in os.walk(zoneinfo):
    #    zones.extend([
    #            os.path.join(dirpath,f) for f in filenames
    #            if not f.endswith('.tab')
    #            ])
    #stripnum = len(os.path.commonprefix(zones))
    #zones = [z[stripnum:] for z in zones]

    for zone in zones:
        name = 'test_' + zone.replace('/','_')
        def test(self,zone=zone):
            self._test_matchzdump(zone)
        setattr(cls,name,test)

fillZDumpTest(cls=ZDumpTransitionTimesTestCase)

if __name__ == '__main__':
    unittest.main()

