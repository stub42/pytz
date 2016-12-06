'''
datetime.tzinfo timezone definitions generated from the
Olson timezone database:

    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz

See the datetime section of the Python Library Reference for information
on how to use these modules.
'''

# The IANA (nee Olson) database is updated several times a year.
OLSON_VERSION = '2016j'
VERSION = '2016.10'  # Switching to pip compatible version numbering.
__version__ = VERSION

OLSEN_VERSION = OLSON_VERSION # Old releases had this misspelling

__all__ = [
    'timezone', 'utc', 'country_timezones', 'country_names',
    'AmbiguousTimeError', 'InvalidTimeError',
    'NonExistentTimeError', 'UnknownTimeZoneError',
    'all_timezones', 'all_timezones_set',
    'common_timezones', 'common_timezones_set',
    ]

import sys, datetime, os.path, gettext

from pytz.exceptions import AmbiguousTimeError
from pytz.exceptions import InvalidTimeError
from pytz.exceptions import NonExistentTimeError
from pytz.exceptions import UnknownTimeZoneError
from pytz.lazy import LazyDict, LazyList, LazySet
from pytz.tzinfo import unpickler
from pytz.tzfile import build_tzinfo, _byte_string


try:
    unicode

except NameError: # Python 3.x

    # Python 3.x doesn't have unicode(), making writing code
    # for Python 2.3 and Python 3.x a pain.
    unicode = str

    def ascii(s):
        r"""
        >>> ascii('Hello')
        'Hello'
        >>> ascii('\N{TRADE MARK SIGN}') #doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        UnicodeEncodeError: ...
        """
        s.encode('ASCII') # Raise an exception if not ASCII
        return s # But return the original string - not a byte string.

else: # Python 2.x

    def ascii(s):
        r"""
        >>> ascii('Hello')
        'Hello'
        >>> ascii(u'Hello')
        'Hello'
        >>> ascii(u'\N{TRADE MARK SIGN}') #doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        UnicodeEncodeError: ...
        """
        return s.encode('ASCII')


def open_resource(name):
    """Open a resource from the zoneinfo subdir for reading.

    Uses the pkg_resources module if available and no standard file
    found at the calculated location.
    """
    name_parts = name.lstrip('/').split('/')
    for part in name_parts:
        if part == os.path.pardir or os.path.sep in part:
            raise ValueError('Bad path segment: %r' % part)
    filename = os.path.join(os.path.dirname(__file__),
                            'zoneinfo', *name_parts)
    if not os.path.exists(filename):
        # http://bugs.launchpad.net/bugs/383171 - we avoid using this
        # unless absolutely necessary to help when a broken version of
        # pkg_resources is installed.
        try:
            from pkg_resources import resource_stream
        except ImportError:
            resource_stream = None

        if resource_stream is not None:
            return resource_stream(__name__, 'zoneinfo/' + name)
    return open(filename, 'rb')


def resource_exists(name):
    """Return true if the given resource exists"""
    try:
        open_resource(name).close()
        return True
    except IOError:
        return False


# Enable this when we get some translations?
# We want an i18n API that is useful to programs using Python's gettext
# module, as well as the Zope3 i18n package. Perhaps we should just provide
# the POT file and translations, and leave it up to callers to make use
# of them.
#
# t = gettext.translation(
#         'pytz', os.path.join(os.path.dirname(__file__), 'locales'),
#         fallback=True
#         )
# def _(timezone_name):
#     """Translate a timezone name using the current locale, returning Unicode"""
#     return t.ugettext(timezone_name)


_tzinfo_cache = {}

def timezone(zone):
    r''' Return a datetime.tzinfo implementation for the given timezone

    >>> from datetime import datetime, timedelta
    >>> utc = timezone('UTC')
    >>> eastern = timezone('US/Eastern')
    >>> eastern.zone
    'US/Eastern'
    >>> timezone(unicode('US/Eastern')) is eastern
    True
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

    Raises UnknownTimeZoneError if passed an unknown zone.

    >>> try:
    ...     timezone('Asia/Shangri-La')
    ... except UnknownTimeZoneError:
    ...     print('Unknown')
    Unknown

    >>> try:
    ...     timezone(unicode('\N{TRADE MARK SIGN}'))
    ... except UnknownTimeZoneError:
    ...     print('Unknown')
    Unknown

    '''
    if zone.upper() == 'UTC':
        return utc

    try:
        zone = ascii(zone)
    except UnicodeEncodeError:
        # All valid timezones are ASCII
        raise UnknownTimeZoneError(zone)

    zone = _unmunge_zone(zone)
    if zone not in _tzinfo_cache:
        if zone in all_timezones_set:
            fp = open_resource(zone)
            try:
                _tzinfo_cache[zone] = build_tzinfo(zone, fp)
            finally:
                fp.close()
        else:
            raise UnknownTimeZoneError(zone)

    return _tzinfo_cache[zone]


def _unmunge_zone(zone):
    """Undo the time zone name munging done by older versions of pytz."""
    return zone.replace('_plus_', '+').replace('_minus_', '-')


ZERO = datetime.timedelta(0)
HOUR = datetime.timedelta(hours=1)


class UTC(datetime.tzinfo):
    """UTC

    Optimized UTC implementation. It unpickles using the single module global
    instance defined beneath this class declaration.
    """
    zone = "UTC"

    _utcoffset = ZERO
    _dst = ZERO
    _tzname = zone

    def fromutc(self, dt):
        if dt.tzinfo is None:
            return self.localize(dt)
        return super(utc.__class__, self).fromutc(dt)

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

    def __reduce__(self):
        return _UTC, ()

    def localize(self, dt, is_dst=False):
        '''Convert naive time to local time'''
        if dt.tzinfo is not None:
            raise ValueError('Not naive datetime (tzinfo is already set)')
        return dt.replace(tzinfo=self)

    def normalize(self, dt, is_dst=False):
        '''Correct the timezone information on the given datetime'''
        if dt.tzinfo is self:
            return dt
        if dt.tzinfo is None:
            raise ValueError('Naive time - no tzinfo set')
        return dt.astimezone(self)

    def __repr__(self):
        return "<UTC>"

    def __str__(self):
        return "UTC"


UTC = utc = UTC()  # UTC is a singleton


def _UTC():
    """Factory function for utc unpickling.

    Makes sure that unpickling a utc instance always returns the same
    module global.

    These examples belong in the UTC class above, but it is obscured; or in
    the README.txt, but we are not depending on Python 2.4 so integrating
    the README.txt examples with the unit tests is not trivial.

    >>> import datetime, pickle
    >>> dt = datetime.datetime(2005, 3, 1, 14, 13, 21, tzinfo=utc)
    >>> naive = dt.replace(tzinfo=None)
    >>> p = pickle.dumps(dt, 1)
    >>> naive_p = pickle.dumps(naive, 1)
    >>> len(p) - len(naive_p)
    17
    >>> new = pickle.loads(p)
    >>> new == dt
    True
    >>> new is dt
    False
    >>> new.tzinfo is dt.tzinfo
    True
    >>> utc is UTC is timezone('UTC')
    True
    >>> utc is timezone('GMT')
    False
    """
    return utc
_UTC.__safe_for_unpickling__ = True


def _p(*args):
    """Factory function for unpickling pytz tzinfo instances.

    Just a wrapper around tzinfo.unpickler to save a few bytes in each pickle
    by shortening the path.
    """
    return unpickler(*args)
_p.__safe_for_unpickling__ = True



class _CountryTimezoneDict(LazyDict):
    """Map ISO 3166 country code to a list of timezone names commonly used
    in that country.

    iso3166_code is the two letter code used to identify the country.

    >>> def print_list(list_of_strings):
    ...     'We use a helper so doctests work under Python 2.3 -> 3.x'
    ...     for s in list_of_strings:
    ...         print(s)

    >>> print_list(country_timezones['nz'])
    Pacific/Auckland
    Pacific/Chatham
    >>> print_list(country_timezones['ch'])
    Europe/Zurich
    >>> print_list(country_timezones['CH'])
    Europe/Zurich
    >>> print_list(country_timezones[unicode('ch')])
    Europe/Zurich
    >>> print_list(country_timezones['XXX'])
    Traceback (most recent call last):
    ...
    KeyError: 'XXX'

    Previously, this information was exposed as a function rather than a
    dictionary. This is still supported::

    >>> print_list(country_timezones('nz'))
    Pacific/Auckland
    Pacific/Chatham
    """
    def __call__(self, iso3166_code):
        """Backwards compatibility."""
        return self[iso3166_code]

    def _fill(self):
        data = {}
        zone_tab = open_resource('zone.tab')
        try:
            for line in zone_tab:
                line = line.decode('UTF-8')
                if line.startswith('#'):
                    continue
                code, coordinates, zone = line.split(None, 4)[:3]
                if zone not in all_timezones_set:
                    continue
                try:
                    data[code].append(zone)
                except KeyError:
                    data[code] = [zone]
            self.data = data
        finally:
            zone_tab.close()

country_timezones = _CountryTimezoneDict()


class _CountryNameDict(LazyDict):
    '''Dictionary proving ISO3166 code -> English name.

    >>> print(country_names['au'])
    Australia
    '''
    def _fill(self):
        data = {}
        zone_tab = open_resource('iso3166.tab')
        try:
            for line in zone_tab.readlines():
                line = line.decode('UTF-8')
                if line.startswith('#'):
                    continue
                code, name = line.split(None, 1)
                data[code] = name.strip()
            self.data = data
        finally:
            zone_tab.close()

country_names = _CountryNameDict()


# Time-zone info based solely on fixed offsets

class _FixedOffset(datetime.tzinfo):

    zone = None # to match the standard pytz API

    def __init__(self, minutes):
        if abs(minutes) >= 1440:
            raise ValueError("absolute offset is too large", minutes)
        self._minutes = minutes
        self._offset = datetime.timedelta(minutes=minutes)

    def utcoffset(self, dt):
        return self._offset

    def __reduce__(self):
        return FixedOffset, (self._minutes, )

    def dst(self, dt):
        return ZERO

    def tzname(self, dt):
        return None

    def __repr__(self):
        return 'pytz.FixedOffset(%d)' % self._minutes

    def localize(self, dt, is_dst=False):
        '''Convert naive time to local time'''
        if dt.tzinfo is not None:
            raise ValueError('Not naive datetime (tzinfo is already set)')
        return dt.replace(tzinfo=self)

    def normalize(self, dt, is_dst=False):
        '''Correct the timezone information on the given datetime'''
        if dt.tzinfo is self:
            return dt
        if dt.tzinfo is None:
            raise ValueError('Naive time - no tzinfo set')
        return dt.astimezone(self)


def FixedOffset(offset, _tzinfos = {}):
    """return a fixed-offset timezone based off a number of minutes.

        >>> one = FixedOffset(-330)
        >>> one
        pytz.FixedOffset(-330)
        >>> one.utcoffset(datetime.datetime.now())
        datetime.timedelta(-1, 66600)
        >>> one.dst(datetime.datetime.now())
        datetime.timedelta(0)

        >>> two = FixedOffset(1380)
        >>> two
        pytz.FixedOffset(1380)
        >>> two.utcoffset(datetime.datetime.now())
        datetime.timedelta(0, 82800)
        >>> two.dst(datetime.datetime.now())
        datetime.timedelta(0)

    The datetime.timedelta must be between the range of -1 and 1 day,
    non-inclusive.

        >>> FixedOffset(1440)
        Traceback (most recent call last):
        ...
        ValueError: ('absolute offset is too large', 1440)

        >>> FixedOffset(-1440)
        Traceback (most recent call last):
        ...
        ValueError: ('absolute offset is too large', -1440)

    An offset of 0 is special-cased to return UTC.

        >>> FixedOffset(0) is UTC
        True

    There should always be only one instance of a FixedOffset per timedelta.
    This should be true for multiple creation calls.

        >>> FixedOffset(-330) is one
        True
        >>> FixedOffset(1380) is two
        True

    It should also be true for pickling.

        >>> import pickle
        >>> pickle.loads(pickle.dumps(one)) is one
        True
        >>> pickle.loads(pickle.dumps(two)) is two
        True
    """
    if offset == 0:
        return UTC

    info = _tzinfos.get(offset)
    if info is None:
        # We haven't seen this one before. we need to save it.

        # Use setdefault to avoid a race condition and make sure we have
        # only one
        info = _tzinfos.setdefault(offset, _FixedOffset(offset))

    return info

FixedOffset.__safe_for_unpickling__ = True


def _test():
    import doctest, os, sys
    sys.path.insert(0, os.pardir)
    import pytz
    return doctest.testmod(pytz)

if __name__ == '__main__':
    _test()

