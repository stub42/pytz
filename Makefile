# Build the pytz libraries
#

MAKE=make
PYTHON24=python2.4
PYTHON25=python2.5
PYTHON26=python2.6
PYTHON27=python2.7
PYTHON31=python3.1
PYTHON32=python3.2
PYTHON=${PYTHON26}
PYTHON3=${PYTHON32}
OLSON=./elsie.nci.nih.gov
TESTARGS=-vv
TARGET=
#TARGET=Europe/Amsterdam Europe/Moscow W-SU Etc/GMT+2 Atlantic/South_Georgia Europe/Warsaw Europe/Vilnius
#Mideast/Riyadh87
STYLESHEET=/usr/share/python-docutils/stylesheets/default.css

all: dist

check: test_tzinfo test_docs

build: build/dist/locales/pytz.pot

dist: build/dist/locales/pytz.pot .stamp-dist
.stamp-dist: .stamp-tzinfo
	cd build/dist && mkdir -p ../tarballs && \
	${PYTHON} setup.py sdist --dist-dir ../tarballs \
	    --formats=bztar,gztar,zip && \
	${PYTHON24} setup.py bdist_egg --dist-dir=../tarballs && \
	${PYTHON25} setup.py bdist_egg --dist-dir=../tarballs && \
	${PYTHON26} setup.py bdist_egg --dist-dir=../tarballs && \
	${PYTHON27} setup.py bdist_egg --dist-dir=../tarballs && \
	${PYTHON31} setup.py bdist_egg --dist-dir=../tarballs && \
	${PYTHON32} setup.py bdist_egg --dist-dir=../tarballs
	touch $@

upload: dist build/dist/locales/pytz.pot .stamp-upload
.stamp-upload: .stamp-tzinfo
	cd build/dist && \
	${PYTHON} setup.py register sdist \
	    --formats=bztar,gztar,zip --dist-dir=../tarballs \
	    upload --sign && \
	${PYTHON24} setup.py register bdist_egg --dist-dir=../tarballs \
	    upload --sign && \
	${PYTHON25} setup.py register bdist_egg --dist-dir=../tarballs \
	    upload --sign && \
	${PYTHON26} setup.py register bdist_egg --dist-dir=../tarballs \
	    upload --sign && \
	${PYTHON27} setup.py register bdist_egg --dist-dir=../tarballs \
	    upload --sign && \
	${PYTHON31} setup.py register bdist_egg --dist-dir=../tarballs \
	    upload --sign && \
	${PYTHON32} setup.py register bdist_egg --dist-dir=../tarballs \
	    upload --sign
	touch $@

test: test_tzinfo test_docs test_zdump

clean:
	rm -f .stamp-*
	rm -rf build/*/*
	make -C ${OLSON}/src clean
	find . -name \*.pyc | xargs rm -f

test_tzinfo: .stamp-tzinfo
	cd build/dist/pytz/tests \
	    && ${PYTHON24} test_tzinfo.py ${TESTARGS} \
	    && ${PYTHON25} test_tzinfo.py ${TESTARGS} \
	    && ${PYTHON26} test_tzinfo.py ${TESTARGS} \
	    && ${PYTHON27} test_tzinfo.py ${TESTARGS} \
	    && ${PYTHON31} test_tzinfo.py ${TESTARGS} \
	    && ${PYTHON32} test_tzinfo.py ${TESTARGS}

test_docs: .stamp-tzinfo
	cd build/dist/pytz/tests \
	    && ${PYTHON24} test_docs.py ${TESTARGS} \
	    && ${PYTHON25} test_docs.py ${TESTARGS} \
	    && ${PYTHON26} test_docs.py ${TESTARGS} \
	    && ${PYTHON27} test_docs.py ${TESTARGS} \
	    && ${PYTHON31} test_docs.py ${TESTARGS} \
	    && ${PYTHON32} test_docs.py ${TESTARGS}

test_zdump: dist
	${PYTHON} gen_tests.py ${TARGET} && \
	${PYTHON} test_zdump.py ${TESTARGS} && \
	${PYTHON3} test_zdump.py ${TESTARGS}

build/dist/test_zdump.py: .stamp-zoneinfo


docs: dist
	mkdir -p build/docs/source/.static
	mkdir -p build/docs/built
	cp src/README.txt build/docs/source/index.txt
	cp conf.py build/docs/source/conf.py
	sphinx-build build/docs/source build/docs/built


.stamp-tzinfo: .stamp-zoneinfo gen_tzinfo.py build/etc/zoneinfo/GMT
	${PYTHON} gen_tzinfo.py ${TARGET}
	rm -rf build/dist/pytz/zoneinfo
	cp -a build/etc/zoneinfo build/dist/pytz/zoneinfo
	touch $@

.stamp-zoneinfo:
	${MAKE} -C ${OLSON}/src TOPDIR=`pwd`/build install
	touch $@

build/dist/locales/pytz.pot: .stamp-tzinfo
	@: #${PYTHON} gen_pot.py build/dist/pytz/locales/pytz.pot

#	cd build/dist; mkdir locales; \
#	pygettext --extract-all --no-location \
#	    --default-domain=pytz --output-dir=locales



.PHONY: all check dist test test_tzinfo test_docs test_zdump
