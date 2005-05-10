# Build the pytz libraries
#

MAKE=make
PYTHON=python2.3
OLSEN=./elsie.nci.nih.gov

tz: build/etc/zoneinfo/UTC FORCE
	${PYTHON} gen_tzinfo.py; ${PYTHON} gen_tests.py

build/etc/zoneinfo/UTC: ${OLSEN}/src/africa build
	${MAKE} -C ${OLSEN}/src TOPDIR=`pwd`/build install

clean:
	rm -rf build; make -C ${OLSEN}/src clean

test: tz FORCE
	cd build && ${PYTHON} ../test_tzinfo.py -v

build:
	mkdir build

FORCE:

