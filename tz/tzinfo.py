#!/usr/bin/env python
'''
$Id: tzinfo.py,v 1.4 2004/05/31 20:44:35 zenzen Exp $
'''

__rcs_id__  = '$Id: tzinfo.py,v 1.4 2004/05/31 20:44:35 zenzen Exp $'
__version__ = '$Revision: 1.4 $'[11:-2]

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
    _transition_times = None
    _transition_info = None
    _zone = None

    def _lastTransition(self, dt):
        dt = dt.replace(tzinfo=None)
        idx = max(0, bisect_right(self._transition_times, dt) - 1)
        return self._transition_info[idx]
        
    def utcoffset(self, dt):
        return self._lastTransition(dt)[0]

    def dst(self, dt):
        return self._lastTransition(dt)[1]

    def tzname(self, dt):
        return self._lastTransition(dt)[2]

    def __repr__(self):
        return '<DstTzInfo %r>' % (self._zone,)
