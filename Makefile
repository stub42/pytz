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

all: dist

# skip test_zdump, since it fails on AMD64, and takes a long time on i386
check: test_tzinfo test_docs

dist: build/dist/locales/pytz.pot .stamp-dist
.stamp-dist: .stamp-tzinfo
	cd build/dist && mkdir -p ../tarballs && \
	${PYTHON} setup.py sdist --dist-dir ../tarballs \
	    --formats=bztar,gztar,zip
	${PYTHON} setup.py bdist_egg 
	touch $@

upload: build/dist/locales/pytz.pot .stamp-upload
.stamp-upload: .stamp-tzinfo
	cd build/dist && \
	${PYTHON} setup.py sdist \
	    --formats=bztar,gztar,zip upload --sign && \
	${PYTHON} setup.py bdist_egg upload --sign && \
	touch $@

test: test_tzinfo test_docs test_zdump

clean:
	rm -f .stamp-*
	rm -rf build/{etc,lib,man,tarballs}
	find build/dist -name \*.py | xargs -r rm
	rm -f build/dist/*.txt build/dist/MANIFEST* build/dist/zone.tab
	make -C ${OLSON}/src clean
	find . -name \*.pyc | xargs rm -f

test_tzinfo: .stamp-tzinfo
	cd build/dist/pytz/tests && ${PYTHON} test_tzinfo.py ${TESTARGS}

test_docs: .stamp-tzinfo
	cd build/dist/pytz/tests && ${PYTHON} test_docs.py ${TESTARGS}

test_zdump: build/dist/test_zdump.py
	${PYTHON} -c \
	    'import compileall;compileall.compile_dir("build/dist/zoneinfo")'
	cd build/dist && ${PYTHON} test_zdump.py ${TESTARGS}

build/dist/test_zdump.py: .stamp-zoneinfo
	${PYTHON} gen_tests.py ${TARGET}

README.html: test_docs
	rst2html --embed-stylesheet --stylesheet-path=${STYLESHEET} \
	    src/README.txt > README.html

.stamp-tzinfo: .stamp-zoneinfo gen_tzinfo.py build/etc/zoneinfo/GMT
	${PYTHON} gen_tzinfo.py ${TARGET}
	cp ${OLSON}/src/zone.tab build/dist/pytz/
	chmod u+w build/dist/pytz/zone.tab
	touch $@

.stamp-zoneinfo:
	${MAKE} -C ${OLSON}/src TOPDIR=`pwd`/build install
	touch $@

build/dist/locales/pytz.pot: .stamp-tzinfo
	${PYTHON} gen_pot.py build/dist/pytz/locales/pytz.pot

#	cd build/dist; mkdir locales; \
#	pygettext --extract-all --no-location \
#	    --default-domain=pytz --output-dir=locales



.PHONY: all check dist test test_tzinfo test_docs test_zdump
