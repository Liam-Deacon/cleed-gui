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
**iv.py** - defines classes for containing LEED IV curve data.
'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

import os.path
from copy import deepcopy
from index import MillerIndex

EXPERIMENTAL_IV, THEORETICAL_IV, UNKNOWN_IV = range(3)

class IVCurve(object): 
    def __init__(self, path=None, data=[], type=None):
        self.data = data or [[],[]]
        self.path = path
        self.type = type
    
    @property
    def type(self):
        return self._iv_type
    
    @type.setter
    def type(self, type):
        if type in [EXPERIMENTAL_IV, THEORETICAL_IV]:
            self._iv_type = type
        elif type is None:
            self._iv_type = UNKNOWN_IV
        else:
            raise ValueError('IV type must be either EXPERIMENTAL_IV or '
                             'THEORETICAL_IV')
    
    @property
    def path(self):
        return self._path
    
    @path.setter
    def path(self, path):
        if isinstance(path, str):
            self._path = path
        elif path is None:
            self._path = ''
        else:
            raise TypeError('path must be str() or None')
            
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, data):
        if isinstance(data, dict):
            self.data = [data['x'], data['y']]
        else:
            self._data = [data[0], data[1]]
    
    @property
    def x(self):
        return self.data[0]
    
    @property
    def y(self):
        return self.data[1]

    def valid_path(self):
        raise NotImplementedError
        
    def load_data(self, path=None):
        '''load iv data from file'''
        filename = path or self.path
        if not filename:
            if self.filename:
                filename = self.filename
            else:
                raise IOError('filename cannot be empty or None')
            
        try:
            import numpy as np
            
            self.data = np.loadtxt(filename, dtype=float, 
                                   comments='#', delimiter=' ')
        except ImportError:
            with open(filename, 'r') as f:
                lines = [line.lstrip().rstrip('#').rstrip() for line in f
                         if not line.lstrip().startswith('#')]
                x = [0] * len(lines)
                y = [0] * len(lines)
                for i, line in enumerate(lines):
                    x[i], y[i], = [t(s) for (t, s) in zip((float, float), 
                                                          line.split())] 
            self.data = [x, y]
        except IOError:
            raise IOError("Unable to open IV file: '%s'" % filename) 

    def smooth(self, method=None, *args, **kwargs):
        '''Returns a smoothed version of the IV curve'''
        smoothed_iv = deepcopy(self)
        x, y = smoothed_iv.data

        method = method or 'fft'      
        try:
            if method.lower() == 'savitzky-golay':
                from scipy.signal import savgol_filter
                y_smoothed = savgol_filter(y, *args, **kwargs)
            else:
                import numpy as np
            
                rft = np.fft.rfft(y)
                fft_cutoff = 4
                fft_tailoff = 0
                rft[fft_cutoff:len(rft) - fft_tailoff] = 0  # frequencies above cutoff are not included
                y_smooth = np.fft.irfft(rft)
            
                smoothed_iv.data = (x, y_smooth)
            
        except ImportError:
            raise NotImplementedError
        
        return smoothed_iv

class IVCurvePair(object):
    def __init__(self, 
                 experiment=None, 
                 theory=None,
                 index=[], 
                 id=None, 
                 weight=1., 
                 used=True):
        self.experiment = experiment or IVCurve()
        self.theory = theory or IVCurve()
        self.id = id
        self.weight = weight
        self.used = used
        self.index = index
    
    def control_string(self):
        if self.used:
            return ('ef:{ef}:ti={ti}:id={id}:wt={wt}'
                    ''.format(ef=self.experiment.path, 
                              ti=self.index,
                              id=self.id,
                              wt=self.weight))
        else:
            return ''
    
    @property
    def index(self):
        return self._index
    
    @index.setter
    def index(self, index):
        if isinstance(index, MillerIndex):
            self._index = index
        else:
            try:
                self._index = MillerIndex(*index[:2])
            except any as e:
                raise e
    
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, id):
        try:
            self._id = int(id)
        except:
            self._id = None
        
    @property
    def weight(self):
        return self._weight
    
    @weight.setter
    def weight(self, weight):
        try:
            if weight >= 0. and weight <= 1.:
                self._weight = float(weight)
            else:
                raise ValueError("weight must be between 0 and 1")
        except any as e:
            raise e
        
    @property
    def used(self):
        return self._used
    
    @used.setter
    def used(self, used):
        self._used = bool(used)
        
    @property
    def rfactor(self):
        return self._rfactor
    
    @rfactor.setter
    def rfactor(self, value):
        if value >= 0. and value <= 1.:
            self._rfactor = float(value)
        else:
            raise ValueError('RFactor must have a value between 0 and 1') 
    
    @property
    def overlap(self):
        overlap = list(set(self.experiment.x) & set(self.theory.x))
        return overlap[1] - overlap[0]
    

class IVCurveGroup(object):
    def __init__(self, 
                 group_name=None, 
                 datasets=[], 
                 theta=0., 
                 phi=0., 
                 group_id=0):
        self.theta = theta
        self.phi = phi
        self.datasets = datasets
        self.id = group_id
        self.name = group_name
        
    @property
    def name(self):
        return self._group_name or str(self.id)
        
    @property
    def id(self):
        return self._group_id
            
    @property 
    def theta(self):
        return self._theta
    
    @property
    def phi(self):
        return self._phi
    
    @property
    def datasets(self):
        return self._iv_pairs
    
    @id.setter
    def id(self, group_id):
        self._group_id = int(group_id) if group_id is not None else 0
    
    @theta.setter
    def theta(self, theta):
        self._theta = float(theta) % 360.
        
    @phi.setter
    def phi(self, phi):
        self._phi = float(phi) % 360.
        
    @datasets.setter
    def datasets(self, iv_pairs):
        self._iv_pairs = [iv_pair for iv_pair in set(iv_pairs) 
                          if isinstance(iv_pair, IVCurvePair)]
        
    @name.setter
    def name(self, name):
        self._group_name = str(name)
    