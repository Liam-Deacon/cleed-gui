#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, with_statement, 
                        print_function, division)
import sys, os

# attempt to add project root to PYTHONPATH
_pkgdir = os.path.dirname(os.path.abspath(__file__))
_pardir = os.path.dirname(_pkgdir)
_rootdir = os.path.dirname(_pardir)  # level above cleed_gui package

for _dir in (_pkgdir, _pardir, _rootdir):
    if _dir not in sys.path:
        sys.path.append(_dir)
    
del(_pkgdir, _pardir, _rootdir)