import unittest
from tzinfo import TZInfo
from datetime import datetime,timedelta,tzinfo
from time import strptime # Need to confirm strptime always available in 2.3
import pickle

class TZInfoTestCase(unittest.TestCase):
    pass

class UTC(tzinfo):
    _notime = timedelta(0)
    def utcoffset(self,dt):
        return self._notime
    def dst(self,dt):
        return self._notime
    def tzname(self,dt):
        return 'UTC'
utc = UTC()

class UTCTestCase(TZInfoTestCase):
    def test_UTC(self):
        UTC = TZInfo('UTC')
        now = datetime.now(tz=UTC)
        self.failUnless(now.utcoffset() == timedelta(0))
        self.failUnless(now.dst() == timedelta(0))
        self.failUnless(now.timetuple() == now.utctimetuple())


class USEasternDSTStartTestCase(TZInfoTestCase):
    tzinfo = TZInfo('US/Eastern')

    # 24 hours before DST kicks in
    dayBefore = datetime(2002, 4, 6, 7, 0, 0, tzinfo=utc)
    #dayBefore = datetime(2002, 4, 6, 2, 0, 0, tzinfo=tzinfo)

    # before transition
    before_tzname = 'EST'
    before_utcoffset = timedelta(hours = -5)
    before_dst = timedelta(hours = 0)

    # after transition
    after_tzname = 'EDT'
    after_utcoffset = timedelta(hours = -4)
    after_dst = timedelta(hours = 1)

    def _test_tzname(self,dt,tzname):
        dt = dt.replace(tzinfo=self.tzinfo)
        self.failUnlessEqual(dt.tzname(),tzname,
            'Expected %s as tzname for %s. Got %s' % (
                tzname,str(dt),dt.tzname()
                )
            )

    def _test_utcoffset(self,dt,utcoffset):
        dt = dt.replace(tzinfo=self.tzinfo)
        self.failUnlessEqual(dt.utcoffset(),utcoffset,
            'Expected %s as utcoffset for %s. Got %s' % (
                utcoffset,dt,dt.utcoffset()
                )
            )

    def _test_dst(self,dt,dst):
        dt = dt.replace(tzinfo=self.tzinfo)
        self.failUnlessEqual(dt.dst(),dst,
            'Expected %s as dst for %s. Got %s' % (
                dst,dt,dt.dst()
                )
            )

    def test_dayBefore_tzname(self):
        self._test_tzname(self.dayBefore, self.before_tzname)

    def test_dayBefore_utcoffset(self):
        self._test_utcoffset(self.dayBefore, self.before_utcoffset)

    def test_dayBefore_dst(self):
        self._test_dst(self.dayBefore, self.before_dst)

    def test_instantAfter_tzname(self):
        self._test_tzname(self.dayBefore + timedelta(days=1), self.after_tzname)

    def test_instantAfter_utcoffset(self):
        self._test_utcoffset(
            self.dayBefore + timedelta(days=1), self.after_utcoffset
            )

    def test_instantAfter_dst(self):
        self._test_dst(self.dayBefore + timedelta(days=1), self.after_dst)

    def test_dayAfter_tzname(self):
        self._test_tzname(self.dayBefore + timedelta(days=2), self.after_tzname)

    def test_dayAfter_utcoffset(self):
        self._test_utcoffset(
            self.dayBefore + timedelta(days=2), self.after_utcoffset
            )

    def test_dayAfter_dst(self):
        self._test_dst(self.dayBefore + timedelta(days=2), self.after_dst)

    def test_leadup(self):
        # Test every second for 15 minutes before
        # This test should probably be disabled as it looks like some
        # OS's kick DST in a few minutes before they should (eg. this
        # test shows Mac OS X 10.2 switching to DST in at 1:57am
        for i in range(int(1.25*60*60),1,-1):
            delta = timedelta(days=1,seconds=-i)
            self._test_dst(self.dayBefore + delta, self.before_dst)
            self._test_utcoffset(self.dayBefore + delta, self.before_utcoffset)
            self._test_tzname(self.dayBefore + delta, self.before_tzname)

    def test_followthrough(self):
        # Test every second for some time after
        # Might need to disable this one as well as test_leadup
        for i in xrange(int(1.25*60*60),1,-1):
            self._test_dst(
                self.dayBefore + timedelta(days=1,seconds=i), self.after_dst
                )
            self._test_utcoffset(
                self.dayBefore + timedelta(days=1,seconds=i), 
                self.after_utcoffset
                )
            self._test_tzname(
                self.dayBefore + timedelta(days=1,seconds=i), self.after_tzname
                )


class USEasternDSTEndTestCase(USEasternDSTStartTestCase):
    tzinfo = TZInfo('US/Eastern')
    #dayBefore = datetime(2002, 10, 26, 2, 0, 0, tzinfo=tzinfo)
    dayBefore = datetime(2002, 10, 26, 6, 0, 0, tzinfo=utc)
    before_tzname = 'EDT'
    before_utcoffset = timedelta(hours = -4)
    before_dst = timedelta(hours = 1)
    after_tzname = 'EST'
    after_utcoffset = timedelta(hours = -5)
    after_dst = timedelta(hours = 0)


'''
class UnknownTimezoneTestCase(TZInfoTestCase):
    def test_UnknownTimezone(self):
        # Unknown timezones should fall back to UTC. We have no choice about
        # this, as this is what the Posix calls do.
        moon = TZInfo('Luna/Tycho')
        moonnow = datetime.now(tz=moon)
        self.failUnless(moonnow.utcoffset() == timedelta(0))
'''

'''
class BulkTransitionTimesTestCase(TZInfoTestCase):
    def setUp(self):
        TZInfoTestCase.setUp(self)

        global raw_boundaries

        tzinfos = {}
        self.boundaries = []

        UTC = TZInfo('UTC')

        fmt = '%a %b %d %H:%M:%S %Y'

        for line in raw_boundaries.split('\n'):
            if not line.strip(): 
                continue
            zone,rest = line.split(' ',1)
            utc_string,rest = rest.split(' = ')
            loc_string,loc_dst = rest.split(' isdst=')
            loc_dst = int(loc_dst)

            utc_string = utc_string.strip()
            loc_string = loc_string.strip()

            utc_tuple = strptime(utc_string[:-4],fmt)
            loc_tuple = strptime(loc_string[:-4],fmt)

            if utc_tuple.tm_sec == 59:
                fudge = -1
            else:
                fudge = 1

            loc_tzname = loc_string.split(' ')[-1]

            if not tzinfos.has_key(zone):
                tzinfos[zone] = TZInfo(zone)
            loc_tzinfo = tzinfos[zone]
            
            utc_dt = datetime(*utc_tuple[:6] + (0,UTC))
            loc_dt = datetime(*loc_tuple[:6] + (0,loc_tzinfo))
            utc_dt = utc_dt + timedelta(hours=fudge*3)
            loc_dt = loc_dt + timedelta(hours=fudge*3)

            self.boundaries.append((utc_dt,loc_dt,loc_dst,zone,loc_tzname,line))

    def test_LocalToUTC(self):
        # Strictly speaking, this shouldn't be here as it is actually
        # testing the datetime class
        for utc_dt,loc_dt,loc_dst,loc_zone,loc_tzname,line in self.boundaries:
            self.failUnlessEqual(utc_dt.timetuple(), loc_dt.utctimetuple())

    def test_UTCToLocal(self):
        # Strictly speaking, this shouldn't be here as it is actually
        # testing the datetime class
        for utc_dt,loc_dt,loc_dst,loc_zone,loc_tzname,line in self.boundaries:
            self.failUnlessEqual(
                loc_dt.timetuple(),
                utc_dt.astimezone(loc_dt.tzinfo).timetuple()
                )

    def test_tzname(self):
        for utc_dt,loc_dt,loc_dst,loc_zone,loc_tzname,line in self.boundaries:
            self.failUnlessEqual(loc_dt.tzname(),loc_tzname)

    def test_dst(self):
        for utc_dt,loc_dt,loc_dst,loc_zone,loc_tzname,line in self.boundaries:
            # Check flag set correctly
            self.failUnlessEqual(
                loc_dt.dst() == timedelta(seconds=0),
                loc_dst == 0
                )
            # Confirm dst offset is correct if we are in dst
            # We know all timezones in the boundaries have a 1 hour DST offset.
            self.failUnlessEqual(
                loc_dt.dst() == timedelta(minutes=60),
                loc_dst == 1
                )

    def test_UTCOffset(self):
        for utc_dt,loc_dt,loc_dst,loc_zone,loc_tzname,line in self.boundaries:
            if loc_zone.startswith('Aus') and loc_dst:
                self.failUnlessEqual(loc_dt.utcoffset(),timedelta(hours = 11))
            elif loc_zone.startswith('Aus') and not loc_dst:
                self.failUnlessEqual(loc_dt.utcoffset(),timedelta(hours = 10))
            elif loc_zone.startswith('US') and loc_tzname == 'EST':
                self.failUnlessEqual(loc_dt.utcoffset(),timedelta(hours = -5))
            elif loc_zone.startswith('US') and loc_tzname == 'EDT':
                self.failUnlessEqual(loc_dt.utcoffset(),timedelta(hours = -4))
            elif loc_zone.startswith('Eu') and loc_tzname == 'CET':
                self.failUnlessEqual(loc_dt.utcoffset(),timedelta(hours = 1))
            elif loc_zone.startswith('Eu') and loc_tzname == 'CEST':
                self.failUnlessEqual(loc_dt.utcoffset(),timedelta(hours = 2))
            else:
                self.fail('Unknown zone/tzname combination %s/%s' % (
                    loc_zone,loc_tzname
                    ))

    def test_pickle(self):
        for utc_dt,loc_dt,loc_dst,loc_zone,loc_tzname,line in self.boundaries:
            p = pickle.dumps(loc_dt)
            unpickled_loc_dt = pickle.loads(p)
            self.failUnlessEqual(loc_dt,unpickled_loc_dt)
'''

# Information provided by zdump(1).
# Trimmed to a small subset that hopefully all modern OS's will get right.
raw_boundaries = '''
Australia/Melbourne Sat Mar 30 15:59:59 2002 GMT = Sun Mar 31 02:59:59 2002 EST isdst=1
Australia/Melbourne Sat Mar 30 16:00:00 2002 GMT = Sun Mar 31 02:00:00 2002 EST isdst=0
Australia/Melbourne Sat Oct 26 15:59:59 2002 GMT = Sun Oct 27 01:59:59 2002 EST isdst=0
Australia/Melbourne Sat Oct 26 16:00:00 2002 GMT = Sun Oct 27 03:00:00 2002 EST isdst=1
Australia/Melbourne Sat Mar 29 15:59:59 2003 GMT = Sun Mar 30 02:59:59 2003 EST isdst=1
Australia/Melbourne Sat Mar 29 16:00:00 2003 GMT = Sun Mar 30 02:00:00 2003 EST isdst=0
Australia/Melbourne Sat Oct 25 15:59:59 2003 GMT = Sun Oct 26 01:59:59 2003 EST isdst=0
Australia/Melbourne Sat Oct 25 16:00:00 2003 GMT = Sun Oct 26 03:00:00 2003 EST isdst=1
Australia/Melbourne Mon Jan 18 03:14:07 2038 GMT = Mon Jan 18 14:14:07 2038 EST isdst=1
Australia/Melbourne Tue Jan 19 03:14:07 2038 GMT = Tue Jan 19 14:14:07 2038 EST isdst=1
US/Eastern          Sun Apr 25 06:59:59 1971 GMT = Sun Apr 25 01:59:59 1971 EST isdst=0
US/Eastern          Sun Apr 25 07:00:00 1971 GMT = Sun Apr 25 03:00:00 1971 EDT isdst=1
US/Eastern          Sun Oct 31 05:59:59 1971 GMT = Sun Oct 31 01:59:59 1971 EDT isdst=1
US/Eastern          Sun Oct 31 06:00:00 1971 GMT = Sun Oct 31 01:00:00 1971 EST isdst=0
US/Eastern          Sun Apr  7 06:59:59 2002 GMT = Sun Apr  7 01:59:59 2002 EST isdst=0
US/Eastern          Sun Apr  7 07:00:00 2002 GMT = Sun Apr  7 03:00:00 2002 EDT isdst=1
US/Eastern          Sun Oct 27 05:59:59 2002 GMT = Sun Oct 27 01:59:59 2002 EDT isdst=1
US/Eastern          Sun Oct 27 06:00:00 2002 GMT = Sun Oct 27 01:00:00 2002 EST isdst=0
US/Eastern          Sun Apr  6 06:59:59 2003 GMT = Sun Apr  6 01:59:59 2003 EST isdst=0
US/Eastern          Sun Apr  6 07:00:00 2003 GMT = Sun Apr  6 03:00:00 2003 EDT isdst=1
US/Eastern          Sun Oct 26 05:59:59 2003 GMT = Sun Oct 26 01:59:59 2003 EDT isdst=1
US/Eastern          Sun Oct 26 06:00:00 2003 GMT = Sun Oct 26 01:00:00 2003 EST isdst=0
Europe/Amsterdam    Sun Mar 31 00:59:59 2002 GMT = Sun Mar 31 01:59:59 2002 CET isdst=0
Europe/Amsterdam    Sun Mar 31 01:00:00 2002 GMT = Sun Mar 31 03:00:00 2002 CEST isdst=1
Europe/Amsterdam    Sun Oct 27 00:59:59 2002 GMT = Sun Oct 27 02:59:59 2002 CEST isdst=1
Europe/Amsterdam    Sun Oct 27 01:00:00 2002 GMT = Sun Oct 27 02:00:00 2002 CET isdst=0
Europe/Amsterdam    Sun Mar 30 00:59:59 2003 GMT = Sun Mar 30 01:59:59 2003 CET isdst=0
Europe/Amsterdam    Sun Mar 30 01:00:00 2003 GMT = Sun Mar 30 03:00:00 2003 CEST isdst=1
Europe/Amsterdam    Sun Oct 26 00:59:59 2003 GMT = Sun Oct 26 02:59:59 2003 CEST isdst=1
Europe/Amsterdam    Sun Oct 26 01:00:00 2003 GMT = Sun Oct 26 02:00:00 2003 CET isdst=0
'''

if __name__ == '__main__':
    unittest.main()

