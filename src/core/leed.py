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
leed.py - implements core LEED classes and functions for data processing.
'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

try:
    from cyorderedict import OrderedDict
except:
    assert ImportWarning("failed to import cyorderedict "
                         "- falling back to collections version")
    from collections import OrderedDict

from collections import MutableMapping

from index import MillerIndex
from iv import IVCurve, IVCurveGroup

class Beam(MillerIndex, IVCurve):
    def __init__(self, *args, **kwargs):
        self.intensity = kwargs.pop('intensity', 1.)
        self.scale_factor = kwargs.pop('scaling', 1.)
        IVCurve.__init__(self, data=kwargs.pop('data', []), 
                         type=IVCurve.THEORETICAL_IV, 
                         smoothed=kwargs.pop('smoothed', True))
        MillerIndex.__init__(self, *args, **kwargs)
    
    def __str__(self):
        sf = str('{}*'.format(self.scale_factor) 
                 if abs(self.scale_factor) != 1. else '-' 
                 if self.scale_factor < 0 else '')
        return "{}{}".format(sf, MillerIndex.__str__(self))
    
    def __repr__(self):
        module = self.__class__.__module__ 
        module = module if module != '__main__' else None
        if module is None or module == str.__class__.__module__:
            name = self.__class__.__name__
        else:
            name = module + '.' + self.__class__.__name__
        return ("{}(h={}, k={}, scaling={}, intensity={})"
                "".format(name,
                          self.h, self.k, self.scale_factor, self.intensity))
    
    def __lt__(self, other):
        return MillerIndex.__lt__(self, other)

    def __gt__(self, other):
        return MillerIndex.__gt__(self, other)
    
    def __le__(self, other):
        return MillerIndex.__le__(self, other)
    
    def __ge__(self, other):
        return MillerIndex.__ge__(self, other)
    
    def __len__(self):
        return IVCurve.__len__(self)
    
    def __add__(self, other):
        return BeamSet(beams=[self, other])
    
    @property
    def scale_factor(self):
        return self._sf
    
    @scale_factor.setter
    def scale_factor(self, scale_factor):
        self._sf = float(scale_factor)
        
    @property
    def intensity(self):
        return self._intensity
    
    @intensity.setter
    def intensity(self, intensity):
        self._intensity = float(intensity)


class BeamSet(MutableMapping):
    '''
    Convenience class for handling Beam lists 
    
    Notes
    -----
    The class is a custom dictionary of string keys representing the 
    Miller indices of the beam item. Any class with an 'index' attribute 
    can be used as the key, as well as a string or tuple. An `int` key may only 
    be used to retrieve or delete a given key.   
    
    Examples
    --------
    >>> beams = BeamSet(beams="(0, 0)+0.5*(1, 0)")
    >>> beams["(0, 0)"]
    
    '''
    def __init__(self, beams=[], theory_file=None):
        self._beams = OrderedDict()
        self.set_beams(beams, theory_file)
        
    def __str__(self):
        string = '?'.join([str(beam) for beam in set(self.beams) 
                           if isinstance(beam, Beam)])
        i = string.find('?')
        while(i >= 0):
            if string[i+1] == '-':
                string = string.replace('?', '')
            else:
                string = string.replace('?', '+')
            i = string.find('?')
        return string

    def __add__(self, other):
        if isinstance(other, Beam):
            if other.index() not in self:
                # add beam to set
                self[other.index()] = other
                return self
            else:
                raise KeyError('Already have a {} beam in self'
                               ''.format(other.index()))
        elif isinstance(other, BeamSet):
            # return list of beam sets
            return [self, other]
        else:
            raise TypeError('Unsupported \'+\' operation with type {}'
                            ''.format(type(other)))
    
    def __sub__(self, other):
        try:
            self.__delitem__(other)
        except KeyError:
            pass
        finally:
            return self

    def __iadd__(self, other):
        if isinstance(other, Beam):
            if other.index() not in self:
                # add beam to set
                self[other.index()] = other
                return self
            else:
                raise KeyError('Already have a {} beam in self'
                               ''.format(other.index()))
        else:
            raise TypeError('Unsupported \'+\' operation with type {}'
                            ''.format(type(other)))
            
    def __isub__(self, other):
        try:
            self.__delitem__(other)
        except KeyError:
            pass

    def __eq__(self, other):
        return self._beams == other._beams
    
    def __ne__(self, other):
        return self._beams != other._beams
    
    def __lt__(self, other):
        return len(self._beams) < len(other._beams)

    def __gt__(self, other):
        return len(self._beams) > len(other._beams)

    def __le__(self, other):
        return len(self._beams) <= len(other._beams)

    def __ge__(self, other):
        return len(self._beams) >= len(other._beams)

    def __contains__(self, key):
        if isinstance(key, str) or isinstance(key, unicode):
            key = eval(key)
        elif isinstance(key, tuple):
            key = key[0:2]
        elif hasattr(key, 'index'):
            if callable(key.index):
                key = key.index()
            else:
                key = key.index
        return self._beams.__contains__(key)
    
    def __len__(self):
        return len(self._beams)
    
    def __delitem__(self, key):
        if isinstance(key, str) or isinstance(key, unicode):
            key = eval(key)
        elif isinstance(key, int):
            key = self._beams.keys()[key]
        elif hasattr(key, 'index'):
            try:
                if callable(key.index):
                    key = key.index()
                else:
                    key = key.index
            except TypeError:
                pass
        del self._beams[key]
        
    def __iter__(self):
        return iter(self._beams)
    
    def __setitem__(self, key, value):
        if isinstance(key, str) or isinstance(key, unicode):
            key = eval(key)
        elif hasattr(key, 'index'):
            try:
                if callable(key.index):
                    key = key.index()
                else:
                    key = key.index
            except TypeError:
                pass
        if key not in self._beams:
            self._beams[key] = value
        else:
            raise KeyError('{} already in beam set'.format(key)) 
    
    def __getitem__(self, key):
        if isinstance(key, str) or isinstance(key, unicode):
            key = eval(key)
        elif isinstance(key, int):
            key = self._beams.keys()[key]
        elif hasattr(key, 'index'):
            try:
                if callable(key.index):
                    key = key.index()
                else:
                    key = key.index
            except TypeError:
                pass 
        return self._beams.__getitem__(key)
    
    def __reversed__(self):
        return reversed(self._beams)
    
    def __hash__(self):
        return id(self)
    
    def keys(self):
        return self._beams.keys()
    
    def popitem(self):
        return self._beams.pop()
    
    def clear(self):
        return self._beams.clear()
    
    @property
    def beams(self):
        return tuple(self._beams.values())
    
    @classmethod
    def eval(cls, string, theory_file):
        """Evaluates string for LEED beams"""
        beams = OrderedDict()
        n_beams = string.count('(')
        if n_beams != string.count(')'):
            raise ValueError('Number of brackets do not match')
        elif n_beams < 1:
            raise ValueError("No string provided")

        beam_data = {}
        if theory_file:
            try:
                beam_data = IVCurveGroup.read_theory(theory_file)
            except:
                pass

        i_beam = n = 0            
        while(n >= 0 and i_beam < n_beams):
            i = n
            n = string.find('(', i)
            if n < 0:
                break
            sf = -1. if string[i] == '-' else 1.   
            if n != i and i < n-1:
                try:
                    sf = float(string[i:n-1])
                except:
                    pass
            i = n
            n = string.find(')', i)+1
            
            index = eval(string[i:n])
            beam = Beam(h=index[0], k=index[1], scaling=sf)
            
            try:
                beam.data = beam_data[index]
            except KeyError:
                pass

            if index not in beams:
                beams[index] = beam
            else:
                raise KeyError('Index {} already in beam list'
                               ''.format(index))
                
            if n == 0: break
            i_beam += 1
            
        return beams
    
    def set_beams(self, beams, theory_file=None):
        self.clear()  # clear dictionary
        if isinstance(beams, str) or isinstance(beams, unicode):
            # parse control line
            self._beams = self.eval(beams, theory_file)
        else:
            self.clear()
            
            if theory_file:
                try:
                    beam_data = IVCurveGroup.read_theory(theory_file)
                except:
                    beam_data = {}
            
            for beam in beams:
                if isinstance(beam, str) or isinstance(beams, unicode):
                    beam = Beam(*eval(beam))
                elif isinstance(beam, Beam):
                    if beam.data:
                        self[beam.index()] = beam
                        continue
                elif isinstance(beam, MillerIndex):
                    beam = Beam(beam.h, beam.k)
                else:
                    beam = beam(1, 1, *beam)
                index = str(beam)
                try:
                    beam.data = beam_data[beam.index()]
                except KeyError:
                    pass 
                self[beam.index()] = beam               

    @beams.setter
    def beams(self, beams):
        self.set_beams(beams)
    
    def has_index(self, index):
        ''' Returns true if index in beam set '''
        return not all([beam.index() == index for beam in self.beams])
    
    def get_combined_IV(self):
        """ Returns an IVCurve with weighted intensities as a result of 
        the combined beams.
        
        See
        ---
        BeamSet.__str__() : 
            States how the weighted intensities are calculated for the 
            set of beams.
        """
        f = lambda x, y: len(x.y) == len(y.y)
        if all(f(self[i], self[i+1]) for i in range(len(self)-1)):
            try: 
                import numpy as np
                shape = np.shape(self.beams[0].y)
                y = np.zeros(shape)
                for beam in self.beams:
                    y += beam.scale_factor*np.array(beam.y)
                x = self[0].x
            except:
                raise
            iv = IVCurve(data=np.array((x, y)).copy(), 
                           type=IVCurve.THEORETICAL_IV)
            return iv
        else:
            # get unique energies 
            x = []
            for beam in self.beams:
                x += list(beam.x)
            x.sort()
            x = set(x)
            energies = OrderedDict()
            for xi in x:
                energies[xi] = 0.
                
            # now add each beams scaled intensities to dictionary's values
            for beam in self.beams:
                for i, x in enumerate(beam.x):
                    energies[x] = energies[x] + beam.y[i]*beam.scale_factor
                    
            x, y = (energies.keys(), energies.values())
             
        return IVCurve(data=(x, y), type=IVCurve.THEORETICAL_IV)
            

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
    import os
    beams = BeamSet("(0., 0.5)", 
                    os.path.expandvars("%Dropbox%\\LEED_programs\\CLEED\\CLEED_DIS_1309_safe-mod-mgjf\\EXAMPLES\\NIO\\Ni111_2x2O.res"))
    
    print(repr(beams[0]))
    from numpy import array
    print(array(beams[0].data, dtype=float))