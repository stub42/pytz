#!/usr/bin/env python
'''
$Id: tzinfo.py,v 1.5 2004/06/02 19:39:54 zenzen Exp $
'''

__rcs_id__  = '$Id: tzinfo.py,v 1.5 2004/06/02 19:39:54 zenzen Exp $'
__version__ = '$Revision: 1.5 $'[11:-2]

from datetime import datetime, timedelta, tzinfo
from bisect import bisect_right

_timedelta_cache = {}
def memorized_timedelta(seconds):
    '''Create only one instance of each distinct timedelta'''
    try:
        return _timedelta_cache[seconds]
    except KeyError:
        delta = timedelta(seconds=seconds)
        _timedelta_cache[seconds] = delta
        return delta

_datetime_cache = {}
def memorized_datetime(*args):
    '''Create only one instance of each distinct datetime'''
    try:
        return _datetime_cache[args]
    except KeyError:
        dt = datetime(*args)
        _datetime_cache[args] = dt
        return dt

_ttinfo_cache = {}
def memorized_ttinfo(*args):
    '''Create only one instance of each distinct tuple'''
    try:
        return _ttinfo_cache[args]
    except KeyError:
        ttinfo = (
                memorized_timedelta(args[0]),
                memorized_timedelta(args[1]),
                args[2]
                )
        _ttinfo_cache[args] = ttinfo
        return ttinfo

class BaseTzInfo(tzinfo):
    __slots__ = ()
    def __str__(self):
        return self._zone

_notime = memorized_timedelta(0)

class StaticTzInfo(BaseTzInfo):
    __slots__ = ()
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

    def __repr__(self):
        return '<StaticTzInfo %r>' % (self._zone,)

class DstTzInfo(BaseTzInfo):
    __slots__ = ()
    _utc_transition_times = None
    _transition_times = None
    _transition_info = None
    _zone = None

    _tzinfos = None
    _is_dst = False

    def __init__(self, _shadow=None):
        if _shadow is None:
            _shadow = self.__class__(self)
            self._tzinfos = [self, _shadow]
        else:
            self._is_dst = True

    def fromutc(self, dt):
        dt = dt.replace(tzinfo=None)
        idx = max(0, bisect_right(self._utc_transition_times, dt) -1)
        inf = self._transition_info[idx]
        return (dt + inf[0]).replace(tzinfo=self._tzinfos[bool(inf[1])])

    def _lastTransition(self, dt):

        # Locate the nearest transition point to dt
        dt = dt.replace(tzinfo=None)
        idx = max(0, bisect_right(self._utc_transition_times, dt) - 1)

        # However, dt might have been off since the transition point
        # is in UTC (up to 12 hours out) and DST offsets might affect it.
        # The correct transition point is the one closest in time to dt,
        # which will be idx-1, idx or idx+1
        options = [
            (abs(dt - self._utc_transition_times[idx + i]), i)
            for i in range(-1, 2)
            if 0 <= idx + i < len(self._utc_transition_times)
            and bool(self._transition_info[idx + i][1]) == self._is_dst
            ]
        offset = min(options)[1]

        inf = self._transition_info[idx + offset]
        if not bool(self._transition_info[idx + offset][1]) == self._is_dst:
            err = 'Nearest to %r is %r. Options %r, %r, %r. dst is %r' % (
                    dt, self._utc_transition_times[idx+offset],
                    self._utc_transition_times[idx-1],
                    self._utc_transition_times[idx],
                    self._utc_transition_times[idx+1],
                    self._is_dst,
                    )
            raise RuntimeError, err

        if bool(self._transition_info[idx][1]) == self._is_dst:
            return self._transition_info[idx]

        # We got the wrong period, due to utc offsets and dst, however
        # the correct one will be the nearest one.
        diff1 = abs(dt - self._utc_transition_times[idx-1])
        diff2 = abs(dt - self._utc_transition_times[idx+1])
        if diff1 < diff2:
            return self._transition_info[idx-1]
        else:
            return self._transition_info[idx+1]

    def utcoffset(self, dt):
        return self._lastTransition(dt)[0]

    def dst(self, dt):
        return self._lastTransition(dt)[1]

    def tzname(self, dt):
        return self._lastTransition(dt)[2]

    def __repr__(self):
        return '<DstTzInfo %r, is_dst=%r>' % (self._zone,self._is_dst)
