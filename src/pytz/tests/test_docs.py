#!/usr/bin/env python
# -*- coding: ascii -*-

import unittest, os, os.path, sys
from doctest import DocFileSuite
sys.path.insert(0, os.path.join(os.pardir, os.pardir))

locs = [
    'README.txt',
    os.path.join(os.pardir, 'README.txt'),
    os.path.join(os.pardir, os.pardir, 'README.txt'),
    ]
README = None
for loc in locs:
    if os.path.exists(loc):
        README = DocFileSuite(loc)
        break
if README is None:
    raise RuntimeError("Can't locate README.txt")

if __name__ == '__main__':
    unittest.main(defaultTest='README')

