# pytz

Brings the IANA tz database into Python. This library allows accurate and
cross platform timezone calculations.

pytz contains generated code, and this branch generates it. The actual
pytz code and documentation can be found in the src/ directory.

## Usage Information / Documentation

See [the pytz README](src/README.rst).

## pytz for Enterprise

Available as part of the Tidelift Subscription.

The maintainers of pytz and thousands of other packages are working with Tidelift to deliver commercial support and maintenance for the open source dependencies you use to build your applications. Save time, reduce risk, and improve code health, while paying the maintainers of the exact dependencies you use. [Learn more.](https://tidelift.com/subscription/pkg/pypi-pytz?utm_source=pypi-pytz&utm_medium=referral&utm_campaign=enterprise&utm_term=repo)


## Release process ##

    1) Untar upstream tarballs into elsie/src
    2) Update VERSION & OLSON_VERSION in src/pytz/__init__.py, and EXPECTED_VERSION in
       src/pytz/tests/test_tzinfo.py
    3) make test
    4) make dist

