# Build the pytz libraries
#

MAKE=make
PYTHON=python2.3
OLSEN=./elsie.nci.nih.gov
TESTARGS=
TARGET=CST6CDT

tz: build/etc/zoneinfo/UTC FORCE
	${PYTHON} gen_tzinfo.py ${TARGET}; ${PYTHON} gen_tests.py ${TARGET}

build/etc/zoneinfo/UTC: ${OLSEN}/src/africa build
	${MAKE} -C ${OLSEN}/src TOPDIR=`pwd`/build install

clean:
	rm -rf build; make -C ${OLSEN}/src clean; \
	find . -name \*.pyc | xargs rm -f

test: test_tzinfo test_zdump

test_tzinfo: tz FORCE
	cd build/tz && ${PYTHON} test_tzinfo.py ${TESTARGS}

test_zdump: tz FORCE
	cd build/tz && ${PYTHON} test_zdump.py ${TESTARGS}

build:
	mkdir build

FORCE:

