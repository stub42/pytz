# Build the pytz libraries
#

MAKE=make
SHELL=/bin/bash
PYTHON24=python2.4
PYTHON25=python2.5
PYTHON26=python2.6
PYTHON27=python2.7
PYTHON31=python3.1
PYTHON32=python3.2
PYTHON33=python3.3
PYTHON34=python3.4
PYTHON35=python3.5
PYTHON36=python3.6
PYTHON=/usr/bin/python
PYTHON3=/usr/bin/python3
IANA=./tz
IANA_GIT=https://github.com/eggert/tz.git

TESTARGS=-vv
TARGET=
#TARGET=Europe/Amsterdam Europe/Moscow W-SU Etc/GMT+2 Atlantic/South_Georgia Europe/Warsaw Europe/Vilnius
#Mideast/Riyadh87
STYLESHEET=/usr/share/python-docutils/stylesheets/default.css

all: dist

check: test_tzinfo test_docs

build: .stamp-tzinfo


dist: eggs wheels
	cd build/dist && mkdir -p ../tarballs && \
	${PYTHON} setup.py -q sdist --dist-dir ../tarballs \
	    --formats=bztar,gztar,zip

eggs: build
	cd build/dist && mkdir -p ../tarballs
	cd build/dist && ${PYTHON24} setup.py -q bdist_egg --dist-dir=../tarballs
	cd build/dist && ${PYTHON25} setup.py -q bdist_egg --dist-dir=../tarballs
	cd build/dist && ${PYTHON26} setup.py -q bdist_egg --dist-dir=../tarballs
	cd build/dist && ${PYTHON27} setup.py -q bdist_egg --dist-dir=../tarballs
	cd build/dist && ${PYTHON35} setup.py -q bdist_egg --dist-dir=../tarballs
	cd build/dist && ${PYTHON34} setup.py -q bdist_egg --dist-dir=../tarballs
	cd build/dist && ${PYTHON33} setup.py -q bdist_egg --dist-dir=../tarballs

wheels: build
	cd build/dist && mkdir -p ../tarballs
	cd build/dist && ${PYTHON} setup.py -q bdist_wheel --universal --dist-dir=../tarballs
	cd build/dist && ${PYTHON3} setup.py -q bdist_wheel --universal --dist-dir=../tarballs

upload: sign
	cd build/dist && ${PYTHON3} setup.py register
	twine upload build/tarballs/*.{egg,whl,gz,asc}

sign: dist
	rm -f build/tarballs/*.asc
	for f in build/tarballs/*.{egg,whl,zip,bz2,gz} ; do \
	    gpg2 --detach-sign -a $$f; \
	done

test: test_lazy test_tzinfo test_docs test_zdump

clean:
	rm -f .stamp-*
	rm -rf build/*/* zdump.out
	make -C ${IANA} clean
	find . -name \*.pyc | xargs rm -f

test_lazy: .stamp-tzinfo
	cd build/dist/pytz/tests \
	    && ${PYTHON24} test_lazy.py ${TESTARGS} \
	    && ${PYTHON25} test_lazy.py ${TESTARGS} \
	    && ${PYTHON26} test_lazy.py ${TESTARGS} \
	    && ${PYTHON27} test_lazy.py ${TESTARGS} \
	    && ${PYTHON31} test_lazy.py ${TESTARGS} \
	    && ${PYTHON32} test_lazy.py ${TESTARGS} \
	    && ${PYTHON33} test_lazy.py ${TESTARGS} \
	    && ${PYTHON34} test_lazy.py ${TESTARGS} \
	    && ${PYTHON35} test_lazy.py ${TESTARGS} \
	    && ${PYTHON36} test_lazy.py ${TESTARGS}

test_tzinfo: .stamp-tzinfo
	cd build/dist/pytz/tests \
	    && ${PYTHON24} test_tzinfo.py ${TESTARGS} \
	    && ${PYTHON25} test_tzinfo.py ${TESTARGS} \
	    && ${PYTHON26} test_tzinfo.py ${TESTARGS} \
	    && ${PYTHON27} test_tzinfo.py ${TESTARGS} \
	    && ${PYTHON31} test_tzinfo.py ${TESTARGS} \
	    && ${PYTHON32} test_tzinfo.py ${TESTARGS} \
	    && ${PYTHON33} test_tzinfo.py ${TESTARGS} \
	    && ${PYTHON34} test_tzinfo.py ${TESTARGS} \
	    && ${PYTHON35} test_tzinfo.py ${TESTARGS} \
	    && ${PYTHON36} test_tzinfo.py ${TESTARGS}

test_docs: .stamp-tzinfo
	cd build/dist/pytz/tests \
	    && ${PYTHON27} test_docs.py ${TESTARGS} \
	    && ${PYTHON34} test_docs.py ${TESTARGS}

test_zdump: dist
	${PYTHON} gen_tests.py ${TARGET} && \
	${PYTHON} test_zdump.py ${TESTARGS} && \
	${PYTHON3} test_zdump.py ${TESTARGS}

build/dist/test_zdump.py: .stamp-zoneinfo

doc: docs

docs: dist
	mkdir -p build/docs/source/.static
	mkdir -p build/docs/built
	cp src/README.txt build/docs/source/index.txt
	cp conf.py build/docs/source/conf.py
	sphinx-build build/docs/source build/docs/built
	chmod -R og-w build/docs/built
	chmod -R a+rX build/docs/built

upload_docs: upload_docs_pythonhosted upload_docs_sf

upload_docs_sf: docs
	rsync -e ssh -ravP build/docs/built/ \
	    web.sourceforge.net:/home/project-web/pytz/htdocs/

upload_docs_pythonhosted: docs
	cd build/dist \
	    && ${PYTHON} setup.py upload_docs --upload-dir=../docs/built

.stamp-tzinfo: .stamp-zoneinfo gen_tzinfo.py build/etc/zoneinfo/GMT
	${PYTHON} gen_tzinfo.py ${TARGET}
	rm -rf build/dist/pytz/zoneinfo
	cp -a build/etc/zoneinfo build/dist/pytz/zoneinfo
	touch $@

.stamp-zoneinfo:
	${MAKE} -C ${IANA} TOPDIR=`pwd`/build install
	# Break hard links, working around http://bugs.python.org/issue8876.
	for d in zoneinfo zoneinfo-leaps zoneinfo-posix; do \
	    rm -rf `pwd`/build/etc/$$d.tmp; \
	    rsync -a `pwd`/build/etc/$$d/ `pwd`/build/etc/$$d.tmp; \
	    rm -rf `pwd`/build/etc/$$d; \
	    mv `pwd`/build/etc/$$d.tmp `pwd`/build/etc/$$d; \
	done
	touch $@

build/dist/locales/pytz.pot: .stamp-tzinfo
	@: #${PYTHON} gen_pot.py build/dist/pytz/locales/pytz.pot

#	cd build/dist; mkdir locales; \
#	pygettext --extract-all --no-location \
#	    --default-domain=pytz --output-dir=locales

# Switch to using a git subtree of https://github.com/eggert/tz
#
# IANA_URL=http://www.iana.org/time-zones/repository
#
# sync:
# 	cd elsie.nci.nih.gov && \
# 	    rm -f tz{code,data}-latest.tar.gz{,.asc} && \
# 	    wget -S ${IANA_URL}/tzcode-latest.tar.gz && \
# 	    wget -S ${IANA_URL}/tzcode-latest.tar.gz.asc && \
# 	    gpg2 --verify tzcode-latest.tar.gz.asc tzcode-latest.tar.gz && \
# 	    wget -S ${IANA_URL}/tzdata-latest.tar.gz && \
# 	    wget -S ${IANA_URL}/tzdata-latest.tar.gz.asc && \
# 	    gpg2 --verify tzdata-latest.tar.gz.asc tzdata-latest.tar.gz && \
# 	    cd src && \
# 	    tar xzf ../tzcode-latest.tar.gz && \
# 	    tar xzf ../tzdata-latest.tar.gz && \
# 	    echo Done

sync: _sync clean

_sync:
	if [ -n "$(TAG)" ]; then \
	    git subtree pull --prefix=tz --squash $(IANA_GIT) $(TAG) \
		-m "IANA $(TAG)"; \
	else \
	    echo "Usage: make sync TAG=2016f"; \
	fi

.PHONY: all check dist test test_tzinfo test_docs test_zdump eggs wheels build clean sync _sync
