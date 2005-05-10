#!/usr/bin/env python
'''
$Id: gen_tzinfo.py,v 1.3 2004/05/29 15:14:44 zenzen Exp $
'''
import sys, os, os.path, shutil

from glob import glob
from datetime import datetime,timedelta,tzinfo
from tzfile import TZFile
from pprint import pprint
from bisect import bisect_right

def allzones(self):
    ''' Return all available tzfile(5) files in the zoneinfo database '''
    zones = []
    for dirpath, dirnames, filenames in os.walk(zoneinfo):
        zones.extend([os.path.join(dirpath,f) for f in filenames])
    stripnum = len(os.path.commonprefix(zones))
    zones = [z[stripnum:] for z in zones]
    return zones

def dupe_src(destdir):
    ''' Copy ./tz to our dest directory '''
    if not os.path.isdir(destdir):
        os.makedirs(destdir)
    for f in glob(os.path.join('tz','*')):
        if not os.path.isdir(f):
            shutil.copy(f, destdir)

def gen_tzinfo(destdir, zoneinfo, zone):
    ''' Create a .py file for the given timezone '''
    filename = os.path.join(zoneinfo, zone)
    tzfile = TZFile(filename)
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
            print 'Building %s' % f
            open(f, 'w').close()

        
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

__rcs_id__  = '$Id: gen_tzinfo.py,v 1.3 2004/05/29 15:14:44 zenzen Exp $'
__version__ = '$Revision: 1.3 $'[11:-2]

__all__ = ['%(szone)s']

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
        'from tz.tzinfo import memorized_timedelta as timedelta',
        'from tz.tzinfo import memorized_datetime as datetime',
        'from tz.tzinfo import memorized_ttinfo as ttinfo',
        ])

    def __init__(self, zone, transitions):

        self.zone = zone

        # Yech. Our DST transition times need to be in local standard 
        # time rather than UTC :-(

        transition_times = []
        transition_info = []
        for i in range(1,len(transitions)):
            tt = transitions[i][0]
            inf = transitions[i][1:]

            if transitions[i][2]:
                tt = tt + transitions[i-1][1] # Need last non-DST offset
            else:
                tt = tt + transitions[i][1]

            transition_times.append(tt)
            transition_info.append(inf)

        attributes = ['']
        attributes.append('    _zone = %s' % repr(zone))
        attributes.append('')

        attributes.append('    _transition_times = [')
        for tt in transition_times:
            attributes.append('        datetime(%4d, %2d, %2d, %2d, %2d),' % (
                tt.year, tt.month, tt.day, tt.hour, tt.minute
                ))
        attributes.append('        ]')
        attributes.append('')

        attributes.append('    _transition_info = [')
        for delta, dst, tzname in transition_info:
            delta = 24 * 60 * 60 * delta.days + delta.seconds

            attributes.append(
                '        ttinfo(%6s, %d, %6r),' % (delta,int(dst),tzname)
                )
        attributes.append('        ]')
        self.attributes = '\n'.join(attributes)

if __name__ == '__main__':
    _destdir = os.path.join(os.path.abspath(sys.argv[1]), 'tz')
    _zoneinfo = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'build','etc','zoneinfo'
            ))
   
    dupe_src(_destdir)
    gen_tzinfo(_destdir, _zoneinfo, 'UTC')
    gen_tzinfo(_destdir, _zoneinfo, 'US/Eastern')
    gen_inits(_destdir)
