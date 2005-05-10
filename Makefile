# Build the pytz libraries
#

MAKE=make
PYTHON=python2.3
OLSEN=./elsie.nci.nih.gov
TESTARGS=-v
TARGET=
TARGET=Europe/Amsterdam Europe/Moscow W-SU Etc/GMT+2 Atlantic/South_Georgia
#Mideast/Riyadh87

build/dist: build/etc/zoneinfo/UTC gen_tzinfo.py
	${PYTHON} gen_tzinfo.py ${TARGET}

clean:
	rm -rf build; make -C ${OLSEN}/src clean; \
	find . -name \*.pyc | xargs rm -f

build/etc/zoneinfo/UTC: ${OLSEN}/src/africa build
	${MAKE} -C ${OLSEN}/src TOPDIR=`pwd`/build install

test: test_tzinfo test_zdump test_pytz

.mk_test: build/dist gen_tests.py
	${PYTHON} gen_tests.py ${TARGET} && touch .mk_test

test_tzinfo: .mk_test
	cd build/dist/pytz && ${PYTHON} test_tzinfo.py ${TESTARGS}

test_zdump: .mk_test
	cd build/dist && ${PYTHON} test_zdump.py ${TESTARGS}

test_pytz: .mk_test
	cd build/dist/pytz && ${PYTHON} __init__.py ${TESTARGS}

build:
	mkdir build

sdist: build/dist
	cd build/dist && \
	${PYTHON} setup.py sdist --force-manifest --formats=bztar,gztar,zip

#build/pytz.zip:	build/tz
#	cd build && zip -9 -r pytz.zip pytz/__init__.py pytz/tzinfo.py pytz/zoneinfo

FORCE:

