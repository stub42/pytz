
Brings the Olson tz database into Python. This library allows accurate
and cross platform timezone calculations.

This implementation solves the issue of ambiguous times at the end of
daylight savings, which you can read more about in the Python Library
Reference (datetime.tzinfo)

The only remaining inaccuracy is that datetime.strftime only reports
the UTC offset to the nearest minute.

More info than you want to know about timezones:
    http://www.twinsun.com/tz/tz-link.htm

