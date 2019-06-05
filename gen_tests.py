#!/usr/bin/env python
# -*- coding: ascii -*-
'''
$Id: gen_tests.py,v 1.15 2005/01/07 04:51:30 zenzen Exp $
'''
from __future__ import unicode_literals

import os
import os.path
import subprocess
import sys
from io import open

import gen_tzinfo
from gen_tzinfo import allzones

zdump = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'build', 'bin', 'zdump'
))


def main():
    dest_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

    with open(os.path.join(dest_dir, 'zdump.out'), 'w') as datf:
        for zone in allzones():
            print('Collecting zdump(1) output for %s in zdump.out' % (zone,))
            # We don't yet support v2 format tzfile(5) files, so limit
            # the daterange we test against - zdump understands v2 format
            # files and will output historical records we can't cope with
            # otherwise.
            command = [zdump, '-v', '-c', '1902,2038', zone]
            zd_out = subprocess.check_output(command)
            # Skip bogus output on 64bit architectures, per Bug #213816
            lines = [
                line.decode('utf-8').strip() for line in zd_out.splitlines()
                if not line.decode('utf-8').strip().endswith('NULL')]

            for line in lines:
                datf.write(line + '\n')


if __name__ == '__main__':
    try:
        gen_tzinfo.target = sys.argv[1:]
    except IndexError:
        gen_tzinfo.target = None
    main()

# vim: set filetype=python ts=4 sw=4 et
