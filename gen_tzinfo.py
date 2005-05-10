#!/usr/bin/env python
'''
$Id: gen_tzinfo.py,v 1.20 2005/01/07 04:51:30 zenzen Exp $
'''
import sys, os, os.path, shutil

from glob import glob
from datetime import datetime,timedelta,tzinfo
from tzfile import TZFile
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

def gen_tzinfo(destdir, zone):
    ''' Create a .py file for the given timezone '''
    filename = os.path.join(zoneinfo, zone)
    tzfile = TZFile(filename)
    zone = pytz._munge_zone(zone)
    if len(tzfile.transitions) == 0:
        ttinfo = tzfile.ttinfo[0]
        generator = StaticGen(zone, ttinfo[0], ttinfo[2])
    else:
        generator = DstGen(zone, tzfile.transitions)
    out_name = os.path.join(destdir, zone + '.py')
    if not os.path.isdir(os.path.dirname(out_name)):
        os.makedirs(os.path.dirname(out_name))
    generator.write(open(out_name,'w'))

def gen_inits(destdir):
    ''' Create required __init__.py's '''
    for dirpath, dirnames, filenames in os.walk(destdir):
        if '__init__.py' not in filenames:
            f = os.path.join(dirpath, '__init__.py')
            open(f, 'w').close()

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

        
class Gen:
    def write(self, out):
        zone = self.zone
        szone = zone.split('/')[-1]
        base_class = self.base_class
        attributes = self.attributes
        imps = self.imps

        print >> out, """'''tzinfo timezone information for %(zone)s.'''
from pytz.tzinfo import %(base_class)s
%(imps)s

class %(szone)s(%(base_class)s):
    '''%(zone)s timezone definition. See datetime.tzinfo for details'''
%(attributes)s

%(szone)s = %(szone)s()
""" % vars()


class StaticGen(Gen):
    base_class = 'StaticTzInfo'
    imps = '\n'.join([
        'from pytz.tzinfo import memorized_timedelta as timedelta',
        ])

    def __init__(self, zone, utcoffset, tzname):
        self.zone = zone
        self.attributes = '\n'.join([
            '    _zone = %s' % repr(zone),
            '    _utcoffset = timedelta(seconds=%d)' % (
                utcoffset.days*24*60*60 + utcoffset.seconds,
                ),
            '    _tzname = %s' % repr(tzname),
            ])


class DstGen(Gen):
    base_class = 'DstTzInfo'
    imps = '\n'.join([
        'from pytz.tzinfo import memorized_datetime as d',
        'from pytz.tzinfo import memorized_ttinfo as i',
        ])

    def __init__(self, zone, transitions):
        self.zone = zone

        utc_transition_times = []
        transition_times = []
        transition_info = []
        for i in range(0,len(transitions)):
            # transitions[i] == time, delta, dst, tzname

            utc_tt = transitions[i][0]

            inf = transitions[i][1:]

            # seconds offset
            utcoffset = inf[0]
            utcoffset = utcoffset.days*24*60*60 + utcoffset.seconds

            if not inf[1]:
                dst = 0
            else:
                # Locate the last non-dst transition
                for j in range(i-1, -1, -1):
                    prev_trans = transitions[j]
                    if not prev_trans[2]:
                        break
                dst = inf[0] - prev_trans[1] # seconds dstoffset
                dst = dst.seconds + dst.days*86400
            tzname = inf[2]

            # Round utcoffset and dst to the nearest minute or the
            # datetime library will complain. Conversions to these timezones
            # might be up to plus or minus 30 seconds out, but it is
            # the best we can do.
            real_utcoffset = utcoffset
            utcoffset = int((utcoffset+30)/60)*60
            dst = int((dst+30)/60)*60
            utc_transition_times.append(utc_tt)

            transition_info.append( (utcoffset, dst, tzname) )

        attributes = ['']
        attributes.append('    _zone = %s' % repr(zone))
        attributes.append('')

        attributes.append('    _utc_transition_times = [')
        for i in range(0, len(utc_transition_times)):
            tt = utc_transition_times[i]
            delta, dst, tzname = transition_info[i]
            #comment = ' # %6d %5d %s' % transition_info[i]
            comment = '' # Save space
            attributes.append(
                #'        datetime(%4d, %2d, %2d, %2d, %2d, %2d),%s' % (
                'd(%d,%d,%d,%d,%d,%d),%s' % ( # Save space
                    tt.year, tt.month, tt.day, tt.hour, tt.minute, tt.second,
                    comment
                    )
                )
        attributes.append('        ]')
        attributes.append('')

        attributes.append('    _transition_info = [')
        for delta, dst, tzname in transition_info:
            attributes.append(
                #'        ttinfo(%6s, %6d, %6r),' % (delta,dst,tzname)
                'i(%s,%d,%r),' % (delta,dst,tzname) # Save space
                )
        attributes.append('        ]')
        self.attributes = '\n'.join(attributes)
 

def main(destdir):
    _destdir = os.path.join(os.path.abspath(destdir), 'dist')
   
    dupe_src(_destdir)
    for zone in allzones():
        print 'Generating %s.py' % zone
        gen_tzinfo(os.path.join(_destdir, 'pytz', 'zoneinfo'), zone)
    gen_inits(_destdir)
    add_allzones(os.path.join(_destdir, 'pytz', '__init__.py'))

if __name__ == '__main__':
    try:
        target = sys.argv[1:]
    except IndexError:
        target = None
    main('build')

