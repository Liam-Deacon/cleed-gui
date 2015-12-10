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
commandline.py - module for processing CLEED-IV command lines arguments
'''

from argparse import ArgumentParser, RawDescriptionHelpFormatter
import sys
import os
from __builtin__ import __import__

from common import VARS

'''
Class for processing command line arguments for CLEED-IV
'''
class CommandLine(object):
    def __init__(self, args=sys.argv):
        sys.argv.extend(args)
        self.parser = ArgumentParser
        self.parsed_args = []
        self.unparsed_args = []
        
        self._setup_parser()
        self.process_cl_args()
    
    def _setup_parser(self):
        program_name = os.path.basename(VARS['name'])
        program_version = "v%s" % VARS['version']
        program_build_date = str(VARS['date'])
        program_version_message = '%%(prog)s %s (%s)' % (program_version, 
                                                         program_build_date)
        program_shortdesc = "".join(VARS['description'].split("\n")[1:2])
        program_license = """%s
    
          Created by Liam Deacon on %s.
          Copyright 2013-2015 Liam Deacon. All rights reserved.
    
          Licensed under the MIT license (see LICENSE file for details)
    
          Please send your feedback, including bug notifications
          and fixes, to: %s
    
        usage:-
        """ % (program_shortdesc, 
               str(VARS['date']), 
               VARS['contact'])
    
        try:
            # Setup argument parser
            self.parser = ArgumentParser(description=program_license, 
                                formatter_class=RawDescriptionHelpFormatter)
            parser = self.parser
            parser.add_argument('-i', '--import', dest='project', 
                                metavar='<project_path>', 
                                help='Imports an existing CLEED project '
                                'which can be an CLEED input/control/result '
                                'file or an CLEED-IV xml file.')
            parser.add_argument('-l', '--logfile', dest='logfile', 
                                metavar='<logfile>', default='cleed-iv.log', 
                                type=str, help="Specifies the CLEED-IV log "
                                "file [default: %(default)s]")
            parser.add_argument('--leed-program', dest='leed', 
                                metavar='<leed_program>', 
                                default= os.environ.get('CSEARCH_LEED', 'cleed'), 
                                help='Specifies the LEED program to use '
                                '[default: %(default)s]')
            parser.add_argument('--rfactor-program', dest='rfac', 
                                metavar='<rfactor_program>', 
                                default=os.environ.get('CSEARCH_RFAC', 'rfac') , 
                                help='Specifies the R-Factor program to use '
                                '[default: %(default)s]')
            parser.add_argument('--phaseshift-program', dest='phsh', 
                                metavar='<phaseshift_program>', 
                                default=os.environ.get('CLEED_PHASE', 'phsh') , 
                                help='Specifies the phaseshift program to use '
                                '[default: %(default)s]')

            parser.add_argument("-v", "--verbose", dest="verbose", 
                                action="count", help="Set verbosity level. "
                                "[default: %(default)s]")
            parser.add_argument('-V', '--version', action='version', 
                                version=program_version_message)
    
        except:
            raise
    
    def process_cl_args(self):
        self.parsed_args, self.unparsed_args = self.parser.parse_known_args()
        
        return self.parsed_args, self.unparsed_args


if __name__ == '__main__':
    cli = CommandLine()
    parsed_args, unparsed_args = cli.process_cl_args()
    print ("parsed args are:\n", str(parsed_args), 
           "unparsed args are:\n", str(unparsed_args))

    # QApplication expects the first argument to be the program name.
    #qt_args = sys.argv[:1] + unparsed_args
    #app = QtGui.QApplication(qt_args)
    # ... the rest of your handling: `sys.exit(app.exec_())`, etc.