from datetime import datetime,timedelta,tzinfo,MINYEAR
from tzfile import TZFile
from pprint import pprint

import os.path
tzbase = os.path.join('elsie.nci.nih.gov','build','etc','zoneinfo')

_notime = timedelta(0)

class TZInfo(tzinfo):
    def __init__(self,transitions='US/Eastern'):
        if type(transitions) == type(''):
            tzf = TZFile(os.path.join(tzbase,transitions))
            transitions = tzf.transitions_mapping
        self._transitions = transitions
        try:
            self._min_year = min(transitions.keys())
        except ValueError:
            self.utcoffset = lambda dt: _notime
            self.dst = lambda dt: _notime
            self.tzname = lambda dt: 'UTC'

    def _lastTransition(self,dt):
        dt = dt.replace(tzinfo=None)
        year = dt.year

        if year > 2037:
            year = 2037
        elif year < self._min_year:
            year = self._min_year

        possibles = self._transitions[year]
        while dt < possibles[0][0]:
            # last transition is previous year
            year -= 1
            possibles = self._transitions[year]
        for t in possibles[::-1]:
            if dt >= t[0]:
                return t[1]
        raise Error,'Unable to locate nearest DST transition time for %s' % (dt)

    def utcoffset(self, dt):
        return self._lastTransition(dt)[0]

    def dst(self, dt):
        lt = self._lastTransition(dt)
        if lt[1]:
            offsets = [None,None]
            for dt,t in self._transitions[dt.year]:
                offsets[t[1]] = t[0]
            try:
                return offsets[1] - offsets[0]
            except TypeError:
                return None
        else:
            return _notime

    def tzname(self, dt):
        return self._lastTransition(dt)[2]

class Eastern(TZInfo):
    def __init__(self):
        TZInfo.__init__(self,'US/Eastern')

if __name__ == '__main__':
    eastern = TZInfo('US/Eastern')
    pprint(eastern._transitions)
