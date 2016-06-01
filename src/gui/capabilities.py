##############################################################################
# Author: Liam Deacon                                                        #
#                                                                            #
# Contact: liam.m.deacon@gmail.com                                           #
#                                                                            #
# Copyright: Copyright (C) 2016 Liam Deacon                                  #
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
capabilities.py - module for defining global variables to be used elsewhere.
'''

CAPABILITIES = {'enabled': [], 'disabled': []}

# EasyLEED for IV image sequence extraction/manipulation
try:
    import easyleed
    CAPABILITIES['enabled'].append('easyleed')
    del(easyleed)
except ImportError:
    CAPABILITIES['disabled'].append('easyleed')

# PyMol for geometry model visualisation
try:
    import pymol2
    CAPABILITIES['enabled'].append('pymol2')
    del(pymol2)
except ImportError:
    CAPABILITIES['disabled'].append('pymol2')

# phaseshifts for on-the-fly calculation of atomic phase shifts
try:
    import phaseshifts
    CAPABILITIES['enabled'].append('phaseshifts')
    del(phaseshifts)
except ImportError:
    CAPABILITIES['disabled'].append('phaseshifts')
    
try:
    import scipy
    CAPABILITIES['enabled'].append('scipy')
except ImportError:
    CAPABILITIES['disabled'].append('scipy')

# export set of capabilities
__all__ = ['CAPABILITIES']
