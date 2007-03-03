#!/usr/bin/env python
'''
$Id: gen_tzinfo.py,v 1.21 2005/02/15 20:21:38 zenzen Exp $
'''
import sys, os, os.path, shutil

from glob import glob
from datetime import datetime,timedelta,tzinfo
from pprint import pprint
from bisect import bisect_right

sys.path.insert(0, 'src')
import pytz

zoneinfo = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'build','etc','zoneinfo'
        ))

def allzones():
    ''' Return all available tzfile(5) files in the zoneinfo database '''
    zones = []
    for dirpath, dirnames, filenames in os.walk(zoneinfo):
        zones.extend([
                os.path.join(dirpath,f) for f in filenames
                if not f.endswith('.tab')
                ])
    stripnum = len(os.path.commonprefix(zones))
    zones = [z[stripnum:] for z in zones]
   
    if target:
        wanted = target + ['US/Eastern', 'UTC']
        zones = [z for z in zones if z in wanted]
    # Does not cope with Riyadh87-89 - it appears this region went
    # on solar time during this period and their DST offset changed
    # minute to minute (the Olson database could only capture a precision
    # of 5 seconds because of way too many zone changes, so the data isn't
    # 100% accurate anyway).
    # 'Factory' and 'localtime' appear to be Olson reference code specific
    # and are skipped
    zones = [z for z in zones if 'Riyadh8' not in z and z not in [
        'Factory', 'localtime'
        ]]
    zones.sort()
    return zones

def links():
    inf_name = 'elsie.nci.nih.gov/src/backward'
    l = {}
    for line in open(inf_name):
        if line.strip().startswith('#') or not line.strip():
            continue
        link, new_name, old_name = line.split()
        assert link == 'Link', 'Got %s' % repr(line)
    return l

def dupe_src(destdir):
    ''' Copy ./src to our dest directory '''
    if not os.path.isdir(destdir):
        os.makedirs(destdir)
    for f in glob(os.path.join('src','*')):
        if not os.path.isdir(f):
            shutil.copy(f, destdir)

    destdir = os.path.join(destdir, 'pytz')
    if not os.path.isdir(destdir):
        os.makedirs(destdir)
    for f in glob(os.path.join('src','pytz', '*')):
        if not os.path.isdir(f):
            shutil.copy(f, destdir)

    destdir = os.path.join(destdir, 'tests')
    if not os.path.isdir(destdir):
        os.makedirs(destdir)
    for f in glob(os.path.join('src', 'pytz', 'tests', '*')):
        if not os.path.isdir(f):
            shutil.copy(f, destdir)

def add_allzones(filename):
    ''' Append a list of all know timezones to the end of the file '''
    outf = open(filename, 'a')

    obsolete_zones = links().keys()

    cz = [z for z in allzones() if 
        (len(z.split('/')) == 2 or z in ('UTC', 'GMT'))
        and z not in obsolete_zones
        and not z.startswith('SystemV/')
        and not z.startswith('Etc/')
        ]

    print >> outf, 'common_timezones = \\'
    pprint(cz, outf)
    print >> outf

    print >> outf, 'all_timezones = \\'
    pprint(allzones(), outf)
    outf.close()


def main(destdir):
    _destdir = os.path.join(os.path.abspath(destdir), 'dist')
   
    dupe_src(_destdir)
    add_allzones(os.path.join(_destdir, 'pytz', '__init__.py'))

target = None
if __name__ == '__main__':
    
    try:
        target = sys.argv[1:]
    except IndexError:
        target = None
    main('build')

