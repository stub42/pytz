# Build the pytz libraries
#

MAKE=make
PYTHON=python2.3
OLSEN=./elsie.nci.nih.gov
TESTARGS=-v
TARGET=
#TARGET=Europe/Amsterdam Europe/Moscow W-SU Etc/GMT+2 Atlantic/South_Georgia
#Mideast/Riyadh87

build/tz: build/etc/zoneinfo/UTC gen_tzinfo.py
	${PYTHON} gen_tzinfo.py ${TARGET}

clean:
	rm -rf build; make -C ${OLSEN}/src clean; \
	find . -name \*.pyc | xargs rm -f

build/etc/zoneinfo/UTC: ${OLSEN}/src/africa build
	${MAKE} -C ${OLSEN}/src TOPDIR=`pwd`/build install

test: test_tzinfo test_zdump

.mk_test: build/tz/test_tzinfo.py build/tz/test_zdump.py gen_tests.py build/tz
	${PYTHON} gen_tests.py ${TARGET} && touch .mk_test
    

test_tzinfo: .mk_test
	cd build/tz && ${PYTHON} test_tzinfo.py ${TESTARGS}

test_zdump: .mk_test
	cd build/tz && ${PYTHON} test_zdump.py ${TESTARGS}

build:
	mkdir build

FORCE:

