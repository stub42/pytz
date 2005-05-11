# Build the pytz libraries
#

MAKE=make
PYTHON=python2.4
OLSON=./elsie.nci.nih.gov
TESTARGS=-vv
TARGET=
#TARGET=Europe/Amsterdam Europe/Moscow W-SU Etc/GMT+2 Atlantic/South_Georgia Europe/Warsaw Europe/Vilnius
#Mideast/Riyadh87
STYLESHEET=/usr/share/python-docutils/stylesheets/default.css

dist: tzinfo
	cd build/dist && \
	${PYTHON} setup.py sdist --force-manifest --formats=bztar,gztar,zip

test: test_tzinfo test_docs build_test_zdump

clean:
	rm -rf build; make -C ${OLSON}/src clean; \
	find . -name \*.pyc | xargs rm -f

test_tzinfo: tzinfo
	cd build/dist/pytz && ${PYTHON} test_tzinfo.py ${TESTARGS}

test_docs: tzinfo
	cd build/dist && ${PYTHON} test_docs.py ${TESTARGS}

test_zdump: build_test_zdump
	${PYTHON} -c 'import compileall;compileall.compile_dir("build/dist")'
	cd build/dist && ${PYTHON} test_zdump.py ${TESTARGS}

build_test_zdump:
	${PYTHON} gen_tests.py ${TARGET}
	
README.html: test_docs
	rst2html --embed-stylesheet --stylesheet-path=${STYLESHEET} \
 	    src/README.txt > build/dist/README.html

tzinfo: zoneinfo
	${PYTHON} gen_tzinfo.py ${TARGET}

zoneinfo:
	${MAKE} -C ${OLSON}/src TOPDIR=`pwd`/build install

