from __future__ import print_function
import sys
import os.path
import time
from gen_tzinfo import allzones

from pytz import __version__

boilerplate = r"""msgid ""
msgstr ""
"Project-Id-Version: pytz %s\n"
"POT-Creation-Date: %s\n"
"Content-Type: text/plain; charset=UTF-8\n"

""" % (
    __version__,
    time.strftime('%Y-%m-%d %H:%M+UTC', time.gmtime(time.time()))
)


def main():
    assert len(sys.argv) == 2, 'Output file not specified on command line'
    pot_file_name = sys.argv[1]

    if not os.path.exists(os.path.dirname(pot_file_name)):
        os.makedirs(os.path.dirname(pot_file_name))

    pot = open(pot_file_name, 'wb')

    print(boilerplate, file=pot)

    for zone in allzones():
        print('msgid "%s"' % zone, file=pot)
        print('msgstr ""', file=pot)
        print(file=pot)


if __name__ == '__main__':
    main()
