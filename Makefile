# Build the pytz libraries
#

MAKE=make
PYTHON=python2.3
OLSEN=./elsie.nci.nih.gov

tz: ${OLSEN}/etc/zoneinfo FORCE
	${PYTHON} gen_tzinfo.py build

FORCE:

${OLSEN}/etc/zoneinfo: 
	${MAKE} -C ${OLSEN}/src TOPDIR=../../build install

clean:
	rm -rf build/*; make -C ${OLSEN}/src TOPDIR=.. clean

test: tz
	cd build && ${PYTHON} ../test_tzinfo.py
