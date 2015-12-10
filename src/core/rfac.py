#!/usr/local/bin/python2.7
# encoding: utf-8
##############################################################################
# Author: Liam Deacon                                                        #
#                                                                            #
# Contact: liam.deacon@diamond.ac.uk                                         #
#                                                                            #
# Copyright: Copyright (C) 2013-2015 Liam Deacon                             #
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
from django.template.defaultfilters import default
"""
rfac.py - calculate the RFactor for a set of LEED IV curves 

rfac provides a command line utility to access the RFactor calculations 
from the system shell rather than from Python directly. It is intended as 
a drop in substitute for the crfac program by Georg Held, but is written in 
pure Python.

Examples
--------
.. code:: bash
   
   rfac.py --help


"""

from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

import rfactor

def required_length(nmin, nmax):
    """custom action to check range"""
    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not nmin <= len(values) <= nmax:
                msg = 'argument "{f}" requires between '
                '{nmin} and {nmax} arguments'.format(
                    f=self.dest, nmin=nmin, nmax=nmax)
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)
    return RequiredLength

def main(argv=None):
    """Command line options."""

    global VERBOSE

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    # display help if no arguments
    if len(argv) == 1:
        argv.append('--help')
    
    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, 
                                                     program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = """%s

      Created by Liam Deacon on %s.
      Copyright 2013-2015 Liam Deacon. All rights reserved.

      Licensed under the MIT license (see LICENSE file for details)

      Please send your feedback, including bug notifications
      and fixes, to: %s

    usage:-
    """ % (program_shortdesc, str(__date__), __contact__)

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, 
                                formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-a', '--print', dest='group', metavar='group', 
                            default='all',
                            help="specifies which group ID's appear in output."
                            "arguments: \"all\" or \"average\". "
                            "note that only the first two letters are "
                            "significant [default: %(default)s]")
        parser.add_argument('-c', '--control', dest='ctr_file', 
                            metavar='<control file>', required=True, 
                            help="specifies the CLEED control file for averaging "
                            "and assignning data input e.g. '*.ctr'. ")
        parser.add_argument('-o', '--output', dest='out_file', 
                            metavar='<output file>', default=sys.stdout,
                            help="specifies a filename for the R-Factor output"
                            "to be written to. [default: stdout]")
        parser.add_argument('-r', '--rfactor', dest='rfac_type', 
                            metavar='<r_factor>', default='rp',
                            help="specifies a particular R-Factor to be used for"
                            "comparison. Valid arguments are: %s. "
                            "[default: \"%(default)s\"]" % str('"' + 
                                '", "'.join(rfactor.RFACTORS) + '"'))
        parser.add_argument('-s', '--shift', dest='shift', nargs='+',   
                            metavar='<first_shift[,last_shift,step]>',
                            action=required_length(1, 3), type=float,
                            default=(-10, 10, 0.5),
                            help="specifies an energy range for shifting "
                            "experimental and theoretical data with respect "
                            " to each other in eV (E_expt = E_theory + shift). "
                            "Note that it takes 1-3 arguments. "
                            "[default: %(default)s]")
        parser.add_argument('-t', '--theory', dest='res_file', 
                            metavar='<results file>', default=None,
                            help="specify the theoretical LEED results file")
        parser.add_argument("-v", "--potential", dest='potential', 
                            metavar='<Vi>', default=4.0,
                            help="sets the imaginary part of the optical "
                            "potential in eV (used for smoothing and for "
                            "computation of Pendry's R-Factor. "
                            "[default: %(default)s] eV")
        parser.add_argument('-w', '--write', dest='write_basename',
                            metavar='<output basename>', default=None,
                            help="Specifies the basename for the outputted "
                            "IV curves. [default: [0-9][0-9][0-9][e|t].iv]")
        parser.add_argument('-V', '--version', action='version', 
                            version=program_version_message)

        # Process arguments
        args, unknown = parser.parse_known_args()
        
    except:
        raise
    
    raise NotImplementedError("Not yet written pure python code")
    
    
if __name__ == '__main__':
    main(sys.argv)