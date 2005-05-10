#!/usr/bin/env python
'''
$Id: tzinfo.py,v 1.2 2004/06/06 10:07:01 zenzen Exp $
'''

__rcs_id__  = '$Id: tzinfo.py,v 1.2 2004/06/06 10:07:01 zenzen Exp $'
__version__ = '$Revision: 1.2 $'[11:-2]

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

_notime = memorized_timedelta(0)

class BaseTzInfo(tzinfo):
    # Overridden in subclass
    _utcoffset = None
    _tzname = None
    _zone = None

    def __str__(self):
        return self._zone


class StaticTzInfo(BaseTzInfo):
    def utcoffset(self,dt):
        ''' See datetime.tzinfo.utcoffset '''
        return self._utcoffset

    def dst(self,dt):
        ''' See datetime.tzinfo.dst '''
        return _notime

    def tzname(self,dt):
        ''' See datetime.tzinfo.tzname '''
        return self._tzname

    def __repr__(self):
        return '<StaticTzInfo %r>' % (self._zone,)

class DstTzInfo(BaseTzInfo):
    # Overridden in subclass
    _utc_transition_times = None # Sorted list of DST transition times in UTC
    _transition_info = None # [(utcoffset, dstoffset, tzname)] corresponding
                            # to _utc_transition_times entries
    _zone = None

    # Set in __init__
    _tzinfos = None
    _dst = None # DST offset

    def __init__(self, _inf=None, _tzinfos=None):
        if _inf:
            self._tzinfos = _tzinfos
            self._utcoffset, self._dst, self._tzname = _inf
        else:
            _tzinfos = {}
            self._tzinfos = _tzinfos
            self._utcoffset, self._dst, self._tzname = self._transition_info[0]
            _tzinfos[self._transition_info[0]] = self
            for inf in self._transition_info[1:]:
                if not _tzinfos.has_key(inf):
                    _tzinfos[inf] = self.__class__(inf, _tzinfos)

    def fromutc(self, dt):
        ''' See datetime.tzinfo.fromutc '''
        dt = dt.replace(tzinfo=None)
        idx = max(0, bisect_right(self._utc_transition_times, dt) - 1)
        inf = self._transition_info[idx]
        return (dt + inf[0]).replace(tzinfo=self._tzinfos[inf])

    def normalize(self, dt):
        ''' If date arithmetic crosses DST boundaries, the tzinfo
            is not magically adjusted. This method normalizes the
            tzinfo to the correct one.

            >>> import pytz
            >>> from datetime import datetime, timedelta
            >>> eastern = pytz.timezone('US/Eastern')
            >>> utc_dt = datetime(2002, 10, 27, 6, 0, 0, tzinfo=utc)
            >>> loc_dt = utc_dt.astimezone(eastern)
            >>> fmt = '%Y-%m-%d %H:%M:%S %Z (%z)'
            >>> loc_dt.strftime(fmt)
            '2002-10-27 01:00:00 EST (-0500)'
            >>> (loc_dt - timedelta(minutes=10)).strftime(fmt)
            '2002-10-27 00:50:00 EST (-0500)'
            >>> eastern.normalize(loc_dt - timedelta(minutes=10)).strftime(fmt)
            '2002-10-27 01:50:00 EDT (-0400)'
            >>> (loc_dt + timedelta(minutes=10)).strftime(fmt)
            '2002-10-27 01:10:00 EST (-0500)'
        '''
        # Convert dt in localtime to UTC
        offset = dt.tzinfo._utcoffset
        dt = dt.replace(tzinfo=None)
        dt = dt - offset
        # convert it back, and return it
        return self.fromutc(dt)

    def utcoffset(self, dt):
        ''' See datetime.tzinfo.utcoffset '''
        # Round to nearest minute or datetime.strftime will complain
        secs = self._utcoffset.seconds + self._utcoffset.days*86400
        return memorized_timedelta(seconds=int((secs+30)/60)*60)

    def dst(self, dt):
        ''' See datetime.tzinfo.dst '''
        # Round to nearest minute or datetime.strftime will complain
        return memorized_timedelta(seconds=int((self._dst.seconds+30)/60)*60)

    def tzname(self, dt):
        ''' See datetime.tzinfo.tzname '''
        return self._tzname

    def __repr__(self):
        if self._utcoffset > _notime:
            return '<DstTzInfo %r %s+%s>' % (
                    self._zone, self._tzname, self._utcoffset
                )
        else:
            return '<DstTzInfo %r %s%s>' % (
                    self._zone, self._tzname, self._utcoffset
                )
