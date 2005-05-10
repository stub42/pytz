'''
$Id: setup.py,v 1.5 2004/07/25 01:34:20 zenzen Exp $
Distribution setup script
'''

from distutils.core import setup

import pytz, sys, os, os.path

me = 'Stuart Bishop'
memail = 'stuart@stuartbishop.net'
ldesc = '''\
World modern and historical timezone definitions, implemented as
Python tzinfo subclasses suitable for use my Python's datetime module. 
Timezone information was provided by the Olsen Timezone database.
Using these timezone definitions resolves all ambiguous daylight savings
time transitions. All DST trantions have been tested against the reference
implementation of zdump found in the Olsen database to confirm even
the obscure historical cases work. This test suite is available seperatly
as it is rather large (75558 comparisisons), as is the program used
to generate this package.

The Olsen Timezone database is updated roughly four times per year,
usually with obscure and generally unnoticable changes. These files
will be regenerated and rereleased soon after updated editions of the
Olsen database are made available.
'''

packages = ['pytz']
for dirpath, dirname, filenames in os.walk(os.path.join('pytz','zoneinfo')):
    packages.append('.'.join(dirpath.split(os.sep)))

setup (
    name = 'pytz',
    version = pytz.VERSION,
    description = 'World timezone definitions, modern and historical',
    long_description = ldesc,
    author = me,
    author_email = memail,
    maintainer = me,
    maintainer_email = memail,
    url = 'http://pytz.sourceforge.net',
    license = open('LICENSE.txt','r').read(),
    keywords = ['timezone','tzinfo', 'datetime', 'olsen', 'time'],
    packages = packages,
    download_url='http://sourceforge.net/project/showfiles.php?group_id=79122',
    platforms=['Independant'],
    classifiers = [
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )
