#!/usr/bin/env python
'''
$Id: gen_tzinfo.py,v 1.21 2005/02/15 20:21:38 zenzen Exp $
'''
from __future__ import print_function
import sys
import os
import os.path
import shutil

from glob import glob
from pprint import pprint
import re

zoneinfo = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'build', 'etc', 'zoneinfo'
))


def allzones():
    ''' Return all available tzfile(5) files in the zoneinfo database '''
    zones = []
    for dirpath, dirnames, filenames in os.walk(zoneinfo):
        for f in filenames:
            p = os.path.join(dirpath, f)
            if open(p, 'rb').read(4) == b'TZif':
                zones.append(p)
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
        'Factory', 'localtime', 'posixrules']]
    zones.sort()
    assert len(zones) > 0
    return zones


def links():
    '''Mapping of alias -> canonical name'''
    l = {}
    olson_src_files = ['tz/vanguard.zi', 'tz/main.zi', 'tz/rearguard.zi']
    for filename in olson_src_files:
        for line in open(filename, 'r'):
            if line.strip().startswith('#') or not line.strip():
                continue
            match = re.search(r'^\s*Link\s+([\w/\-]+)\s+([\w/\-]+)', line)
            if match is not None:
                new_name = match.group(1)
                old_name = match.group(2)
                l[old_name] = new_name
            else:
                assert not line.startswith('Link'), line
    assert 'Portugal' in l, 'Portugal should be in links()'
    return l


def dupe_src(destdir):
    ''' Copy ./src to our dest directory '''
    if not os.path.isdir(destdir):
        os.makedirs(destdir)
    for f in glob(os.path.join('src', '*')):
        if not os.path.isdir(f):
            shutil.copy(f, destdir)

    destdir = os.path.join(destdir, 'pytz')
    if not os.path.isdir(destdir):
        os.makedirs(destdir)
    for f in glob(os.path.join('src', 'pytz', '*')):
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

    # Calculate 'common' timezones as best we can. We start with all
    # timezones, strip out the legacy noise, and any name linked to
    # a more canonical name (eg. Asia/Singapore is preferred to just
    # Singapore)
    cz = [
        z for z in allzones()
        if (z not in obsolete_zones and
            '/' in z and
            not z.startswith('SystemV/') and
            not z.startswith('Etc/'))]
    # And extend our list manually with stuff we think deserves to be
    # labelled 'common'.
    cz.extend([
        'UTC', 'GMT', 'US/Eastern', 'US/Pacific', 'US/Mountain',
        'US/Central', 'US/Arizona', 'US/Hawaii', 'US/Alaska',
        # Canadian timezones per Bug #506341
        'Canada/Newfoundland', 'Canada/Atlantic', 'Canada/Eastern',
        'Canada/Central', 'Canada/Mountain', 'Canada/Pacific'])
    # And extend out list with all preferred country timezones.
    zone_tab = open(os.path.join(zoneinfo, 'zone.tab'), 'r')
    for line in zone_tab:
        if line.startswith('#'):
            continue
        code, coordinates, zone = line.split(None, 4)[:3]
        if zone not in cz:
            cz.append(zone)
    cz.sort()

    print('_all_timezones_unchecked = \\', file=outf)
    pprint(sorted(allzones()), outf)
    print('''all_timezones = LazyList(
        tz for tz in _all_timezones_unchecked if resource_exists(tz))
        ''', file=outf)
    print('all_timezones_set = LazySet(all_timezones)', file=outf)
    # Per lp:1835784 we can't afford to do this at import time
    # print >> outf, '_all_timezones_lower_to_standard = dict((tz.lower(), tz) for tz in all_timezones)'

    print('common_timezones = \\', file=outf)
    pprint(cz, outf)
    print('''common_timezones = LazyList(
            tz for tz in common_timezones if tz in all_timezones)
        ''', file=outf)
    print('common_timezones_set = LazySet(common_timezones)', file=outf)

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
