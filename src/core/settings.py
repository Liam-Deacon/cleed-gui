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
*settings.py* - module for dealing with general CLEED-GUI application settings.
'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

try:
    import configparser
    from configparser import ExtendedInterpolation
except ImportError:
    import ConfigParser as configparser
    from configparser import ExtendedInterpolation

class CLEEDConfigParser(configparser.SafeConfigParser):
    BOOLEAN_STATES = {'true': True, 'false': False}
    DEFAULT_PATHS = ['CLEED.ini', 'CLEED.cfg', 'cleed.ini', 'cleed.cfg', 
                     'phaseshifts.ini', 'phaseshifts.cfg']
    SECTIONS = {'defaults': ('executables', 
                             'environment', 
                             'extensions'),
                'explorer': (),
                'gui': ('main_window' 
                        'extract_iv',
                        ), 
                'scripting': (),
                'rfactor': (),
                'ivs': (),
                'syntax_highlighter': (),
                'lattice': (),
                'paths': (),
                'pattern': (),
                'phaseshifts': (),
                }
    __parsers = []
    
    def __init__(self, 
                 defaults=None, 
                 dict_type=configparser._default_dict, 
                 allow_no_value=False,
                 interpolation=ExtendedInterpolation()):
        configparser.ConfigParser.__init__(self, defaults=defaults, 
                                           dict_type=dict_type, 
                                           allow_no_value=allow_no_value,
                                           interpolation=interpolation,
                                           strict=True)
    
        for section in self.SECTIONS:
            self.add_section(section)

        # explorer
        
        # extensions
        self.set('extensions', 'bulk', '.bul;.bsr;.bmin')
        self.set('extensions', 'control', '.ctr')
        self.set('extensions', 'error', '.err')
        self.set('extensions', 'input', '.inp;.par;.pmin')
        self.set('extensions', 'iv', '.cur;.iv;.fsm;.xy')
        self.set('extensions', 'lattice', '.latt')
        self.set('extensions', 'leed', '.res')
        self.set('extensions', 'log', '.log')
        self.set('extensions', 'output', '.out')
        self.set('extensions', 'pattern', '.patt')
        self.set('extensions', 'vertex', '.ver;.vbk')
        self.set('extensions', 'mkiv', '.mkiv')
        
        # paths
        self.set('paths', 'cleed', '$CLEED_HOME/bin/cleed')
        
        # scripting
        self.set('scripting', 'history_length', 2000)
        self.set('scripting', 'in_prefix', '>>> ')
        self.set('scripting', 'out_prefix', ' ')
        self.set('scripting', 'colors', 'linux')
        self.set('scripting', 'startup_script', '~/.cleed/init.py')
        self.set('scripting', 'imports', 
                 'numpy as np; scipy as sp; matplotlib as mpl')
    
        
        self.__class__.__parsers.append(self)
        
    def __del__(self):
        self.__class__.__parsers.pop(self)
        
    @classmethod 
    def getParser(cls, instance=-1, **kwargs):
        """ Returns an active instance of the config parser """
        try:
            return cls.__parsers[instance]
        except IndexError:
            return cls(**kwargs)
