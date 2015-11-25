##############################################################################
# Author: Liam Deacon                                                        #
#                                                                            #
# Contact: liam.deacon@diamond.ac.uk                                         #
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
global_vars.py - module for defining global variables to be used elsewhere.
'''

import sys

# Define globals
__APP_AUTHOR__ = 'Liam Deacon'
__APP_COPYRIGHT__ = '\xa9' + '2013-2015 {0}'.format(__APP_AUTHOR__)
__APP_DATE__ = '2015-11-30'
__APP_DESCRIPTION__ = ('CLEED - Interactive Visualiser (IV) \n '
                        '- a GUI front end to the CLEED package')
__APP_DISTRIBUTION__ = 'cleed-gui'
__APP_EMAIL__ = 'liam.m.deacon@gmail.com'
__APP_CONTACT__ = __APP_AUTHOR__ + "<" +__APP_EMAIL__ + ">"
__APP_LICENSE__ = 'GNU General Public License 3.0'
__APP_NAME__ = u'CLEED-IV'
__APP_VERSION__ = '0.1.0-dev'
__PYTHON__ = "{0}.{1}.{2}".format(sys.version_info.major,
                                  sys.version_info.minor,
                                  sys.version_info.micro, 
                                  sys.version_info.releaselevel)
__UPDATE_URL__ = ""

__DEBUG__ = True

VARS = {'author': __APP_AUTHOR__, 
        'copyright': __APP_COPYRIGHT__,
        'contact': __APP_CONTACT__,
        'date': __APP_DATE__,
        'description': __APP_DESCRIPTION__,
        'distribution': __APP_DISTRIBUTION__,
        'email': __APP_EMAIL__,
        'license': __APP_LICENSE__,
        'name': __APP_NAME__,
        'version': __APP_VERSION__,
        'python': __PYTHON__,
        'update url': __UPDATE_URL__,
        'debug': __DEBUG__}