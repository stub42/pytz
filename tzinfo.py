from datetime import datetime,timedelta,tzinfo
from tzfile import TZFile
from pprint import pprint
from bisect import bisect_right

import os.path
zoneinfo = os.path.join(
    os.path.dirname(__file__),'elsie.nci.nih.gov','build','etc','zoneinfo'
    )

def allzones(self):
    ''' Return all available tzfile(5) files in the zoneinfo database '''
    zones = []
    for dirpath, dirnames, filenames in os.walk(zoneinfo):
        zones.extend([os.path.join(dirpath,f) for f in filenames])
    stripnum = len(os.path.commonprefix(zones))
    zones = [z[stripnum:] for z in zones]
    return zones

_notime = timedelta(0)

def TZInfo(zone='UTC'):
    filename = os.path.join(zoneinfo,zone)
    tzfile = TZFile(filename)
    if len(tzfile.transitions) == 0:
        ttinfo = tzfile.ttinfo[0]
        return StaticTzInfo(ttinfo[0],ttinfo[2])
    else:
        return DstTzInfo(tzfile.transitions)

class StaticTzInfo(tzinfo):
    def __init__(self,utcoffset=_notime,tzname='UTC'):
        self._utcoffset = utcoffset
        self._tzname = tzname

    def utcoffset(self,dt):
        return self._utcoffset

    def dst(self,dt):
        return _notime

    def tzname(self,dt):
        return self._tzname

class DstTzInfo(tzinfo):
    def __init__(self,transitions=[]):

        # Yech. Our DST transition times need to be in local standard 
        # time rather than UTC :-(

        self._transition_times = []
        self._transition_info = []
        for i in range(1,len(transitions)):
            tt = transitions[i][0]
            inf = transitions[i][1:]
            tt = tt + transitions[i-1][1] # Need last non-DST offset

            # To convert to local standard time, we take our UTC time
            # and add our nearest non-DST utcoffset
            #if inf[1]:
            #    tt = tt + transitions[i-1][1] # Need last non-DST offset
            #else:
            #    tt = tt + inf[0]

            self._transition_times.append(tt)
            self._transition_info.append(inf)
            
        #self._transition_times = [
        #    transitions[i][0] + transitions[i-1][1]
        #    for i in xrange(1,len(transitions))
        #    ]
        #self._transition_info = [t[1:] for t in transitions[1:]]

        #self._transition_times = [t[0] for t in transitions]
        #self._transition_info = [t[1:] for t in transitions]

        #assert type(t[0]) == type(datetime.now())
        #assert type(t[1]) == type(_notime)
        #assert type(t[2]) == type(True)
        #assert type(t[3]) == type('')

    def _lastTransition(self, dt):
        dt = dt.replace(tzinfo = None)
        idx = max(0,bisect_right(self._transition_times,dt)-1)
        return self._transition_info[idx]
        
    def utcoffset(self, dt):
        rv = self._lastTransition(dt)[0]
        if type(rv) != type(timedelta(0)):
            raise TypeError,'Got a %s' % (str(type(rv)))
        return rv

    def dst(self, dt):
        dt = dt.replace(tzinfo = None)
        dst_idx = max(0,bisect_right(self._transition_times,dt)-1)

        # If not DST, no offset
        if not self._transition_info[dst_idx][1]:
            return _notime

        assert self._transition_info[dst_idx] == self._lastTransition(dt)

        non_idx = dst_idx - 1
            # Currently assumes a DST timezone info always proceeded by non-DST
        non_info = self._transition_info[non_idx]
        while non_info[1]:
            non_idx -= 1
            non_info = self._transition_info[non_idx]

        return self._transition_info[dst_idx][0] - non_info[0]

    def tzname(self, dt):
        return self._lastTransition(dt)[2]


if __name__ == '__main__':
    tz = TZInfo('Australia/Melbourne')
    def show(dt):
        print dt
        print '-> dst() = %r' % (tz.dst(dt))
        print '-> utcoffset() = %r' % (tz.utcoffset(dt))
        print '-> tzname() = %r' % (tz.tzname(dt))
    now = datetime.now(tz=tz)
    show(now)
    then = now + timedelta(days=30*6)
    show(then)


