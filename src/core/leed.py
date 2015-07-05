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

'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

class Params(object):
    '''Provides parameters for LEED calculation'''
    def __init__(self, 
                 vr=-13.0, 
                 vi=4.0, 
                 ei=50., 
                 ef=100.1, 
                 de=1., 
                 ep=1.e-3, 
                 lm=7):
        self.real_potential = vr
        self.imag_potential = vi
        self.start_energy = ei
        self.final_energy = ef
        self.energy_step = de
        self.epsilon = ep
        self.lmax = lm
    
    def __str__(self):
        return ('\n# optical potential:\n'
                'vr: {vr:5.1f}\n'
                'vi: {vi:5.1f}\n'
                '\n# energy range:\n'
                'ei: {ei:5.1f}\n'
                'ef: {ef:5.1f}\n'
                'es: {es:5.1f}\n'
                '\n# search epsilon:\n'
                'ep: {ep:g}\n'
                '\n# lmax of phase shifts:\n'
                'lm: {lm}\n'
                ''.format(vr=self.real_potential, 
                          vi=self.imag_potential, 
                          ei=self.start_energy,
                          ef=self.final_energy,
                          es=self.energy_step,
                          ep=self.epsilon,
                          lm=self.lmax))
    
    @property
    def lmax(self):
        return self._lm
    
    @property 
    def real_potential(self):
        return self._vr
    
    @property
    def imag_potential(self):
        return self._vi
    
    @property
    def start_energy(self):
        return self._ei
    
    @property 
    def final_energy(self):
        return self._ef
    
    @property
    def energy_step(self):
        return self._de
    
    @property
    def epsilon(self):
        return self._ep
    
    @lmax.setter
    def lmax(self, lm):
        if lm < 19 and lm >= 0:
            self._lm = int(lm)
        else:
            raise ValueError('lmax must be between 0 and 18')  # possible 0 bug
    
    @real_potential.setter
    def real_potential(self, vr):
        self._vr = float(vr)
    
    @imag_potential.setter
    def imag_potential(self, vi):
        self._vi = float(vi)
    
    @start_energy.setter
    def start_energy(self, ei):
        self._ei = float(ei)
    
    @final_energy.setter
    def final_energy(self, ef):
        self._ef = float(ef)
    
    @energy_step.setter
    def energy_step(self, de):
        self._de = float(de)
    
    @epsilon.setter
    def epsilon(self, ep):
        self._ep = float(ep)
        
if __name__ == '__main__':
    print(Params())