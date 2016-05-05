#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, with_statement, 
                        print_function, division)
import os, sys

from pkg_resources import get_distribution, DistributionNotFound

__project__ = 'cleed_gui'
__version__ = None  # required for initial installation

try:
    __version__ = get_distribution(__project__).version
except DistributionNotFound:
    VERSION = __project__ + '-' + '(local)'
else:
    VERSION = __project__ + '-' + __version__

# attempt to add package root to PYTHONPATH
_pkgdir = os.path.dirname(os.path.abspath(__file__))
_rootdir = os.path.dirname(_pkgdir)  # level above cleed_gui package

if _rootdir not in sys.path:
    sys.path.append(_root)
    
del(_pkgdir, _root)