
Brings the Olson tz database into Python. This library allows accurate and
cross platform timezone calculations.

More information in src/README.txt

Release process;

    1) Untar upstream tarballs into elsie/src
    2) Update OLSON_VERSION in src/pytz/__init__.py and EXPECTED_VERSION in
       src/pytz/tests/test_tzinfo.py
    3) make test
    4) make dist

