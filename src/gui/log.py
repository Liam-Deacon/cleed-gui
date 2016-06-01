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
**log.py** - module for handling log messages and related items
'''

import logging
from collections import OrderedDict


class LogLevel(object):
    ''' Class for handling log levels 
    
    Attributes:
        LOG_LEVEL_MAX: maximum log level
        LOG_LEVELS: dictionary of level names as keys and integers as values
        DEFAULT_LEVEL: default log level
    '''
    LOG_LEVEL_MAX = 1000
    LOG_LEVELS = OrderedDict((logging.getLevelName(level), level) for level 
                             in range(LOG_LEVEL_MAX) if not 
                             logging.getLevelName(level).startswith("Level"))
    DEFAULT_LEVEL = logging.DEBUG
    
    @staticmethod
    def getLogLevel(level):
        ''' Returns the log level as an integer or default '''
        try:
            level = int(level)
        except ValueError:
            try:
                level = level.upper()
                level = LogLevel.LOG_LEVELS[level]
            except (AttributeError, KeyError):
                level = None 
        return level or LogLevel.DEFAULT_LEVEL
