#!/usr/bin/env python
# -*- coding: ascii -*-

import unittest
from doctest import DocFileSuite

README = DocFileSuite('README.txt')

if __name__ == '__main__':
    unittest.main(defaultTest='README')

