# pytz

Brings the IANA tz database into Python. This library allows accurate and
cross platform timezone calculations.

pytz contains generated code, and this branch generates it. The actual
pytz code and documentation can be found in the src/ directory. More
information about pytz can be found in src/README.txt

Release process:

    1) Untar upstream tarballs into elsie/src
    2) Update VERSION & OLSON_VERSION in src/pytz/__init__.py, and EXPECTED_VERSION in
       src/pytz/tests/test_tzinfo.py
    3) make test
    4) make dist

