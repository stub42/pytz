#!/usr/bin/env python
'''
$Id: gen_tzinfo.py,v 1.5 2004/05/31 20:44:35 zenzen Exp $
'''
import sys, os, os.path, shutil

from glob import glob
from datetime import datetime,timedelta,tzinfo
from tzfile import TZFile
from pprint import pprint
from bisect import bisect_right

import tz

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
    
    # For debugging
    zones = [z for z in zones if z in (
            'US/Eastern', 'Australia/Melbourne', 'UTC'
            )]
    return zones

def dupe_src(destdir):
    ''' Copy ./tz to our dest directory '''
    if not os.path.isdir(destdir):
        os.makedirs(destdir)
    for f in glob(os.path.join('tz','*')):
        if not os.path.isdir(f):
            shutil.copy(f, destdir)

def gen_tzinfo(destdir, zone):
    ''' Create a .py file for the given timezone '''
    filename = os.path.join(zoneinfo, zone)
    tzfile = TZFile(filename)
    zone = tz._munge_zone(zone)
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

    print >> outf, 'timezones = \\'
    pprint(allzones(), outf)
    outf.close()

        
class Gen:
    def write(self, out):
        zone = self.zone
        szone = zone.split('/')[-1]
        base_class = self.base_class
        attributes = self.attributes
        imps = self.imps

        print >> out, """'''
tzinfo timezone information for %(zone)s.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from tz.tzinfo import %(base_class)s
%(imps)s

class %(szone)s(%(base_class)s):
    '''%(zone)s timezone definition. See datetime.tzinfo for details'''
%(attributes)s

%(szone)s = %(szone)s() # Singleton
""" % vars()


class StaticGen(Gen):
    base_class = 'StaticTzInfo'
    imps = '\n'.join([
        'from tz.tzinfo import memorized_timedelta as timedelta',
        ])

    imp = 'from tz.tzinfo import _mem, _mem_clear'

    def __init__(self, zone, utcoffset, tzname):
        self.zone = zone
        self.attributes = '\n'.join([
            '    _zone = %s' % repr(zone),
            '    _utcoffset = timedelta(%d)' % utcoffset.seconds,
            '    _tzname = %s' % repr(tzname),
            ])


class DstGen(Gen):
    base_class = 'DstTzInfo'
    imps = '\n'.join([
        'from tz.tzinfo import memorized_datetime as datetime',
        'from tz.tzinfo import memorized_ttinfo as ttinfo',
        ])

    def __init__(self, zone, transitions):
        self.zone = zone

        # if first transition is in dst, add an extra one before it that
        # isn't
        if transitions[0][2]:
            for nondst in transitions:
                if not nondst[2]:
                    break
            delta = nondst[1]
            dst = nondst[2]
            tzname = nondst[3]
            if delta > timedelta(0):
                transitions.insert(
                        0, (datetime.min, delta, dst, tzname)
                        )
            else:
                transitions.insert(
                        0, (datetime.min - delta, delta, dst, tzname)
                        )

        transition_times = []
        transition_info = []
        for i in range(0,len(transitions)):
            # transitions[i] == time, delta, dst, tzname

            try:
                tt = transitions[i][0] + transitions[i-1][1] # Local, naive time
            except IndexError:
                tt = transitions[i][0] + transitions[i+1][1] # Local, naive time

            tt = transitions[i][0] + transitions[i-1][1] # Local, naive time
            inf = transitions[i][1:]

            # seconds offset
            utcoffset = inf[0]
            utcoffset = utcoffset.days*24*60*60 + utcoffset.seconds

            if not inf[1]:
                dst = 0
            else:
                dst = inf[0] - transitions[i-1][1] # seconds dstoffset
                dst = dst.seconds
            tzname = inf[2]

            if not dst:
                # we are comming out of DST, so we need to adjust the
                # transition time, which is local
                prev_dst = transitions[i-1][1] - inf[0]
                tt = tt - prev_dst
            transition_times.append(tt)
            transition_info.append( (utcoffset, dst, tzname) )

        attributes = ['']
        attributes.append('    _zone = %s' % repr(zone))
        attributes.append('')

        attributes.append('    _transition_times = [')
        for i in range(0, len(transition_times)):
            tt = transition_times[i]
            delta, dst, tzname = transition_info[i]
            comment = ' # %6d %5d %s' % transition_info[i]
            attributes.append(
                '        datetime(%4d, %2d, %2d, %2d, %2d),%s' % (
                    tt.year, tt.month, tt.day, tt.hour, tt.minute, comment
                    )
                )
        attributes.append('        ]')
        attributes.append('')

        attributes.append('    _transition_info = [')
        for delta, dst, tzname in transition_info:
            attributes.append(
                '        ttinfo(%6s, %6d, %6r),' % (delta,dst,tzname)
                )
        attributes.append('        ]')
        self.attributes = '\n'.join(attributes)
 

def main(destdir):
    _destdir = os.path.join(os.path.abspath(destdir), 'tz')
   
    dupe_src(_destdir)
    for zone in allzones():
        gen_tzinfo(_destdir, zone)
    gen_inits(_destdir)
    add_allzones(os.path.join(_destdir, '__init__.py'))

if __name__ == '__main__':
    main('build')

