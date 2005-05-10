#!/usr/bin/env python
'''
$Id: tzinfo.py,v 1.1 2003/06/29 09:22:01 zenzen Exp $
'''

__rcs_id__  = '$Id: tzinfo.py,v 1.1 2003/06/29 09:22:01 zenzen Exp $'
__version__ = '$Revision: 1.1 $'[11:-2]

import datetime as datetime
from bisect import bisect_right

_timedelta_cache = {}
def memorized_timedelta(seconds):
    '''Create only one instance of each distinct timedelta'''
    try:
        return _timedelta_cache[seconds]
    except KeyError:
        delta = datetime.timedelta(seconds)
        _timedelta_cache[seconds] = delta
        return delta

_datetime_cache = {}
def memorized_datetime(*args):
    '''Create only one instance of each distinct datetime'''
    try:
        return _datetime_cache[args]
    except KeyError:
        dt = datetime.datetime(*args)
        _datetime_cache[args] = dt
        return dt

_ttinfo_cache = {}
def memorized_ttinfo(*args):
    '''Create only one instance of each distinct tuple'''
    try:
        return _ttinfo_cache[args]
    except KeyError:
        ttinfo = (memorized_timedelta(args[0]), args[1], args[2])
        _ttinfo_cache[args] = ttinfo
        return ttinfo

class BaseTzInfo(datetime.tzinfo):
    def __str__(self):
        return self._zone

    def __repr__(self):
        return 'tz.' + '.'.join(self._zone.split('/'))

_notime = memorized_timedelta(0)

class StaticTzInfo(BaseTzInfo):
    _utcoffset = None
    _tzname = None
    _zone = None

    def utcoffset(self,dt):
        return self._utcoffset

    def dst(self,dt):
        return _notime

    def tzname(self,dt):
        return self._tzname

    def __call__(self):
        return self # In case anyone thinks this is a Class and not an instance

class DstTzInfo(BaseTzInfo):
    _transition_times = None
    _transition_info = None
    _zone = None

    def _lastTransition(self, dt):
        dt = dt.replace(tzinfo = None)
        idx = max(0,bisect_right(self._transition_times,dt)-1)
        return self._transition_info[idx]
        
    def utcoffset(self, dt):
        print 'Last transition: %r' % (self._lastTransition(dt),)
        rv = self._lastTransition(dt)[0]
        print 'rv: %r' % (rv,)
        if type(rv) != type(_notime):
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

