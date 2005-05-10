pytz - World Timezone Definitions for Python
============================================

Introduction
~~~~~~~~~~~~

pytz brings the Olson tz database into Python. This library allows
accurate and cross platform timezone calculations using Python 2.3 or
higher.

This implementation solves the issue of ambiguous times at the end
of daylight savings, which you can read more about in the Python
Library Reference (datetime.tzinfo). The only remaining inaccuracy
is that datetime.strftime only reports the UTC offset to the nearest
minute (This is probably a feature - you have to draw a line somewhere).

536 of the Olsen timezones are supported. The missing few are for
Riyadh Solar Time in 1987, 1988 and 1989. As Saudi Arabia gave up
trying to cope with their timezone definition, I see no reason
to complicate my code further to cope with them. (I understand
the intention was to set sunset to 0:00 local time, the start of the
Islamic day. In the best case caused the DST offset to change daily 
and worst case caused the DST offset to change each instant depending 
on how you interpreted the ruling.)

Note that if you perform date arithmetic on local times that cross DST
boundaries, the results may be in an incorrect timezone (ie. subtract
1 minute from 2002-10-27 1:00 EST and you get 2002-10-27 0:59 EST instead
of the correct 2002-10-27 1:59 EDT). This cannot be resolved without
modifying the Python datetime implementation. However, these tzinfo
classes provide a normalize() method which allows you to correct these
values.


Installation
~~~~~~~~~~~~

This is a standard Python distutils distribution. To install the
package, run the following command as an administrative user::

    python setup.py install


Example & Usage
~~~~~~~~~~~~~~~

    >>> from datetime import datetime, timedelta
    >>> from pytz import timezone
    >>> utc = timezone('UTC')
    >>> eastern = timezone('US/Eastern')
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


License
~~~~~~~

BSD style license. I'm happy to relicense this code if necessary 
for inclusion in other open source projects.


Latest Versions
~~~~~~~~~~~~~~~

This package will be updated after releases of the Olsen timezone database.
The latest version can be downloaded from sourceforge_. The code that
is used to generate this distribution is available in the sourceforge_
project's CVS repository.

.. _sourceforge: http://sourceforge.net/projects/pytz/


Further Reading
~~~~~~~~~~~~~~~

More info than you want to know about timezones::

    http://www.twinsun.com/tz/tz-link.htm


Contact
~~~~~~~

Stuart Bishop <stuart@stuartbishop.net>

