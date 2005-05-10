#!/usr/bin/env python
# -*- coding: ascii -*-
'''
$Id: test_docs.py,v 1.1 2004/07/24 21:21:28 zenzen Exp $
'''

__rcs_id__  = '$Id: test_docs.py,v 1.1 2004/07/24 21:21:28 zenzen Exp $'
__version__ = '$Revision: 1.1 $'[11:-2]

import doctest

def test_readme(): pass
test_readme.__doc__ = open('README.txt').read()

if __name__ == '__main__':
    doctest.testmod()

# vim: set filetype=python ts=4 sw=4 et

