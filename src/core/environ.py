##############################################################################
# Author: Liam Deacon                                                        #
#                                                                            #
# Contact: liam.m.deacon@gmail.com                                           #
#                                                                            #
# Copyright: Copyright (C) 2014-2015 Liam Deacon                             #
#                                                                            #
# License: MIT License                                                       #
#                                                                            #
# Permission is hereby granted, free of charge, to any person obtaining a    #
# copy of this software and associated documentation files (the "Software"), #
# to deal in the Software without restriction, including without limitation  #
# the rights to use, copy, modify, merge, publish, distribute, sublicense,   #
# and/or sell copies of the Software, and to permit persons to whom the      #
# Software is furnished to do so, subject to the following conditions:       #
#                                                                            #
# The above copyright notice and this permission notice shall be included in #
# all copies or substantial portions of the Software.                        #
#                                                                            #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,   #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL    #
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING    #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER        #
# DEALINGS IN THE SOFTWARE.                                                  #
#                                                                            #
##############################################################################
'''
**environ.py** - defines class for defining CLEED operation environment.
'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

import os

try:
    from phaseshifts.utils import expand_filepath
except ImportError:
    expand_filepath = lambda x: os.path.expanduser(os.path.expandvars(x))


class Environment(object):
    ENVVARS = ['CLEED_HOME', 'CLEED_PHASE', 'CSEARCH_LEED', 'CSEARCH_RFAC']
    
    '''
    Attributes
    ----------
    leed_exe : str
        Path to CLEED executable. 
    rfac_exe : str
        Path to CRFAC executable. 
    search_exe : str
        Path to CSEARCH executable.
    envvars : dict
        Search environment.
    '''
    def __init__(self, leed_exe=None, rfac_exe=None, search_exe=None, **kwargs):
        self.leed_exe = leed_exe
        self.rfac_exe = rfac_exe
        self.search_exe = search_exe
        self.envvars = {}
        self.envvars.update(kwargs)
    
    def _is_executable(self, path):
        return os.access(path, os.X_OK)  
    
    def _is_valid_exe(self, exe):
        return self._is_executable(expand_filepath(exe))
    
    def check_environment(self, keys=ENVVARS):
        is_okay = True
        if keys is not None:
            for var in self.envvars:
                try:
                    if var not in keys:
                        raise KeyError("'{}' environment variable not in {}"
                                       "".format(var, keys))
                        is_okay = False
                except TypeError:
                    raise TypeError("'keys' keyword must be iterable")
                    is_okay = False
        return is_okay
    
    def validate_executables(self):
        return (self._is_valid_exe(self.leed_exe) and 
                self._is_valid_exe(self.rfac_exe) and 
                self._is_valid_exe(self.search_exe))