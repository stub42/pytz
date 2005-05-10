# Build the pytz libraries
#

MAKE=make
PYTHON=python2.3
OLSEN=./elsie.nci.nih.gov
TESTARGS=
TARGET=
#TARGET=Europe/Amsterdam Europe/Moscow W-SU Etc/GMT+2 Atlantic/South_Georgia
#Mideast/Riyadh87
STYLESHEET=../docutils-0.3.3/tools/stylesheets/default.css

build/dist: build/etc/zoneinfo/UTC gen_tzinfo.py src/pytz/tzinfo.py src/pytz/test_tzinfo.py src/README.txt
	${PYTHON} gen_tzinfo.py ${TARGET}

clean:
	rm -rf build; make -C ${OLSEN}/src clean; \
	find . -name \*.pyc | xargs rm -f

build/etc/zoneinfo/UTC: ${OLSEN}/src/africa build
	${MAKE} -C ${OLSEN}/src TOPDIR=`pwd`/build install

test: test_tzinfo test_docs test_zdump

.mk_test: build/dist gen_tests.py
	${PYTHON} gen_tests.py ${TARGET} && touch .mk_test

test_zdump: .mk_test
	cd build/dist && ${PYTHON} test_zdump.py ${TESTARGS}

test_tzinfo: .mk_test
	cd build/dist/pytz && ${PYTHON} test_tzinfo.py ${TESTARGS}

test_docs: .mk_test
	cd build/dist && ${PYTHON} test_docs.py ${TESTARGS}

build:
	mkdir build

dist: sdist


sdist: build/dist build/dist/test_zdump.py.bz2
	cd build/dist && \
	${PYTHON} setup.py sdist --force-manifest --formats=bztar,gztar,zip

build/dist/test_zdump.py.bz2: build/dist
	mkdir -p build/dist/dist
	cd build/dist && bzip2 -c9 < test_zdump.py > dist/test_zdump.py.bz2

README.html: src/README.txt build/dist
	rst2html.py --embed-stylesheet --stylesheet-path=${STYLESHEET} \
	    src/README.txt > build/dist/README.html

FORCE:

