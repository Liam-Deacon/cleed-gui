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
**iv.py** - defines classes for containing LEED IV curve data.
'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

import os.path
import sys
from copy import deepcopy
from index import MillerIndex, MillerIndexSet
from collections import OrderedDict, MutableMapping

class IVCurve(object):
    EXPERIMENTAL_IV, THEORETICAL_IV, UNKNOWN_IV = ('expt', 'theory', None)
    
    def __init__(self, path=None, data=[], **kwargs):
        # crudely mangle load_data function to instance method  
        self._data = []
        
        self.type = kwargs.pop('type', self.UNKNOWN_IV)
        self.path = path

        if path and (data == [] or data == None or len(data)):
            try:
                self.data = self._load_data()
            except:
                self.data = data
        else:
            self.data = data
        self.smoothed = kwargs.pop('smoothed', False)
        self.__dict__.update(kwargs)
    
    def __repr__(self):
        module = self.__class__.__module__ 
        module = module if module != '__main__' else None
        if module is None or module == str.__class__.__module__:
            name = self.__class__.__name__
        else:
            name = module + '.' + self.__class__.__name__
        return ("{}(path={}, data={}, type={})"
                "".format(name, repr(self.path), 
                          repr(self.data), repr(self.type)))
    
    def __len__(self):
        ''' Returns the number of energy values for the IVCurve '''
        return len(self.x)
    
    def __eq__(self, other):
        return self.data == other.data
    
    def __ne__(self, other):
        return self.data != other.data
    
    def __getitem__(self, i):
        if isinstance(i, int):
            return self._data[i]
        elif isinstance(i, float):
            # try to get intensity for given energy value
            try:
                return self.y[self.x.index(i)]
            except AttributeError:
                try:
                    from numpy import where
                    return self.y[where(self.x == i)[0][0]]
                except:
                    return None
            except ValueError:
                return None
    
    def __delitem__(self, i):
        del self._data[i]
        
    def __setitem__(self, i, val):
        self._data[i] = val
        return self._data[i]
    
    @property
    def type(self):
        return self._iv_type
    
    @type.setter
    def type(self, type):
        if type in (self.EXPERIMENTAL_IV, self.THEORETICAL_IV):
            self._iv_type = type
        elif type is None:
            self._iv_type = self.UNKNOWN_IV
        else:
            raise ValueError('IV type must be either {}, {} or {}'
                             ''.format(repr(self.EXPERIMENTAL_IV), 
                                       repr(self.THEORETICAL_IV),
                                       repr(self.UNKNOWN_IV)))
    
    @property
    def path(self):
        return self._path
    
    @path.setter
    def path(self, path):
        if isinstance(path, str) or isinstance(path, unicode):
            self._path = path
        elif path is None:
            self._path = ''
        else:
            raise TypeError('path must be str() or None - got "{}"'
                            ''.format(type(path)))
            
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, data):
        if data == [] or data == None or not len(data):
            return  # shortcut data assignment if no data
        
        if isinstance(data, dict):
            self.data = (data['x'], data['y'])
        else:
            try:
                self._data = data[0:2]
            except:
                import sys
                sys.stderr.write("Could not allocate data '{}' to {}\n"
                                 "".format(repr(data), repr(self)))
    
    @property
    def x(self):
        return self.data[0]
    
    @property
    def y(self):
        return self.data[1]
    
    @classmethod
    def load_data(cls, path=None):
        if not path:
            return []

        try:
            import numpy as np
            
            data = np.genfromtxt(path, dtype=float, comments='#', delimiter=' ')
            data = data.transpose()
            
        except (ImportError, ValueError):
            with open(path, 'r') as f:
                lines = [line.lstrip().rstrip('#').rstrip() for line in f
                         if not line.lstrip().startswith('#')]
                x = [0] * len(lines)
                y = [0] * len(lines)
                for i, line in enumerate(lines):
                    x[i], y[i], = [t(s) for (t, s) in zip((float, float), 
                                                          line.split())] 
            data = (x, y)
        except IOError:
            raise IOError("Unable to open IV file: '%s'" % filename) 
        return data
    
    def _load_data(self, path=None):
        '''load iv data from file'''
        filename = path or self.path
        filename = os.path.expandvars(os.path.expanduser(filename))
        self.data = IVCurve.load_data(filename)
        self.path = filename
    
    def smooth(self, method=None, *args, **kwargs):
        '''Returns a smoothed version of the IV curve'''
        smoothed_iv = deepcopy(self)
        x, y = smoothed_iv.data

        method = method or 'fft'      
        try:
            if method.lower() == 'savitzky-golay':
                from scipy.signal import savgol_filter
                y_smoothed = savgol_filter(y, *args, **kwargs)
            elif method.lower() == 'lorentz':
                self._lorentz_smooth(*args, **kwargs)
            else:
                import numpy as np
            
                rft = np.fft.rfft(y)
                fft_cutoff = 4
                fft_tailoff = 0
                rft[fft_cutoff:len(rft) - fft_tailoff] = 0  # frequencies above cutoff are not included
                y_smooth = np.fft.irfft(rft)
            
                smoothed_iv.data = (x, y_smooth)
                smoothed.smoothed = True
                
        except ImportError:
            raise NotImplementedError
        
        return smoothed_iv
    
    def _lorentz_smooth(self, vi=4.0):
        import numpy as np
        from math import min, max, sqrt
        
        intbuf = np.copy(self.y)
        prefac = [e_step * vi / ((e_step * i)**2 + vi**2) 
                  for i in range(len(self.y))]

        # First check if vi is nonzero
        if vi < 0.001:
            raise ValueError('vi is too small')

        # Sort IV curve if not yet done
        if not self.sorted:
            self.sort()

        # smooth IV curve 
        if self.equidistant:
  
            e_step = self.x[1] - self.x[0]

            if e_step == 0.:
              raise ValueError("energy step is too small")
            
        
            # Find energy range for integral 
            n_range = vi * sqrt((1. / 0.001) - 1.) / e_step
        
            # scan over all energies 
            for i in range(len(self.y)):
                # store original intensities and calculate 
                # first element of integral sum
                self._data[1][i] *= prefac[0]
                norm_sum = prefac[0]
        
                # upper branch: 
                i_hi = min(i+n_range, len(self.x))
                for i_sum in range(i+1 , i_hi):
                    self._data[1][i] += self.y[i_sum] * prefac[i_sum-i]
                    norm_sum += prefac[i_sum-i]
        
                # lower branch: 
                i_lo = max(i - n_range + 1, 0)
                for i_sum in range(i_lo, i):
                    self._data[1][i] += intbuf[i_sum] * prefac[i-i_sum]
                    norm_sum += prefac[i-i_sum] 
        
                # normalize intensity 
                self._data[1][i] /= norm_sum 
        
            # set smooth flag 
            self.smoothed = True
    
    def sort(self):
        ''' Sorts an IV curve according to ascending x '''
        try:
            import numpy as np
            T = np.array(data).transpose()
            ordered = T[np.lexsort((T[:, 0], ))]
            self.data = ordered.transpose()
        except:
            f = lambda x,y: (x, y)
            xy = [f(self.x[i], self.y[i]) for i in range(len(self.data[0]))]
            ordered = sorted(b, key=lambda x:x[0])
            self.data = ([x[0] for x in ordered], [y[1] for y in ordered])
    
    @property
    def equidistant(self):
        diff = lambda x,y: y - x
        x = self.x
        try:
            from numpy import isclose
        except ImportError:
            from is_close import isclose
            
        return all(isclose(diff(x[i], x[i+1]), 
                           diff(x[i+1], x[i+2])) 
                   for i in range(len(x)-2))
    
    @property
    def sorted(self):
         f = lambda x,y: x <= y
         x = self.x
         return all(f(x[i], x[i+1]) for i in range(len(x)-1))
    
    @property
    def smoothed(self):
        return self._smoothed
    
    @smoothed.setter
    def smoothed(self, smoothed):
        self._smoothed = bool(smoothed)
    
    @property
    def max_intensity(self):
        try:
            from numpy import max
            return max(self.y)
        except ImportError:
            from math import max
            maximum = 0.
            for i in self.y:
                maximum = max(maximum, i)
            return maximum
    

class IVCurvePair(object):
    '''
    Class for holding information on an associated pair of IV Curves
    '''
    def __init__(self, 
                 experiment=None, 
                 theory=None,
                 index=[], 
                 id=None, 
                 weight=1., 
                 used=True):
        self.experiment = experiment if isinstance(experiment, IVCurve) else IVCurve()
        self.theory = theory
        self.id = id
        self.weight = weight
        self.used = used
        self.index = index
    
    def __repr__(self):
        module = self.__class__.__module__ 
        module = module if module != '__main__' else None
        if module is None or module == str.__class__.__module__:
            name = self.__class__.__name__
        else:
            name = module + '.' + self.__class__.__name__
        return ("{}(experiment={}, theory={}, index={}, "
                "id={}, weight={}, used={})".format(name,
                                                    repr(self.experiment),
                                                    repr(self.theory),
                                                    self.index,
                                                    repr(self.id),
                                                    repr(self.weight),
                                                    repr(self.used)))
    
    def to_control_string(self):
        return ('{}ef:{ef}:ti={ti}:id={id}:wt={wt}'
                ''.format('#' if self.used else '',
                          ef=self.experiment.path, 
                          ti=self.index,
                          id=self.id,
                          wt=self.weight))
    
    @classmethod
    def from_control_string(cls, ctr_line, ctr_file=None):
        from leed import BeamSet
        ctr_file = os.path.expanduser(os.path.expandvars(ctr_file or ''))
        expand_path  = (lambda x: 
                        (str(x) if os.path.isfile(os.path.expanduser(
                                                os.path.expandvars(str(x))))
                        else os.path.join(os.path.dirname(ctr_file),
                                          os.path.basename(str(x))))) 
        funcs = {'ef': (lambda x: IVCurve(path=expand_path(x), 
                                          type=IVCurve.EXPERIMENTAL_IV)), 
                 'ti': (lambda x: BeamSet(x)), 
                 'id': (lambda x: int(x)), 
                 'wt': (lambda x: float(x))}
    
        mapper = {'ef': 'experiment',
                  'ti': 'index',
                  'id': 'id',
                  'wt': 'weight'}
        
        if ('ef=' not in ctr_line or 
                'ti=' not in ctr_line or 'id=' not in ctr_line):
            return None
            raise ValueError("line '{}' must contain 'ef=', 'ti=' and 'id='"
                             "".format(ctr_line.replace('\n', '')))

        

        used = ctr_line.startswith("#")
        args = ctr_line[used:].split(':')
        kwargs = {}
        for arg in args:
            var, value = arg.split('=')[:2]
            var = var.rstrip()
            value = value.lstrip()
            kwargs[mapper[var]] = funcs[var](value)

        return IVCurvePair(**kwargs) 
        
    @property
    def index(self):
        return self._index
    
    @index.setter
    def index(self, index):
        from leed import BeamSet
        if (isinstance(index, MillerIndex) or 
                isinstance(index, MillerIndexSet) or 
                    isinstance(index, BeamSet)):
            self._index = index
        else:
            try:
                self._index = MillerIndex(*index[:2])
            except any as e:
                try:
                    self._index = MillerIndexSet(index)
                except any as e:
                    raise e
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
    def uniform(self):
        if not self.experiment.data or not self.theory.data:
            return False
        #if not self.experiment.equidistant or self.theory.equidistant:
        #    return False  # shortcircuit further checks
        overlap = self.data_overlap()
        theory, expt = (overlap['theory'], overlap['experiment'])
         
        if len(expt[0]) != len(theory[0]): 
            return False  # short-circuit further checks
        
        dx = lambda x, y: y - x
        uniform = lambda x, y: all(dx(x[i], x[i+1]) == dx(y[i], y[i+1])
                                   for i in range(len(x)-1))
        return uniform(theory[0], expt[0])
    
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
    def energy_overlap(self):
        '''Returns a (start energy, final energy) tuple representing the
        energy overlap between the IV curves '''
        overlap = list(set(self.experiment.x) & set(self.theory.x))
        overlap.sort()
        return (overlap[0], overlap[len(overlap)-1])
    
    def data_overlap(self):
        '''Returns a dictionary containing the overlapping theory 
        and experiment data'''
        e0, ef = self.energy_overlap()
        expt_data = [iv for iv in self.experiment.data 
                     if iv[0] <= ef and iv[0] >= e0]
        theory_data = [iv for iv in self.theory.data 
                       if iv[0] <= ef and iv[0] >= e0]
        return {'theory': theory_data, 'experiment': expt_data}
    
    def interpolate_overlap(self, s=0, der=0):
        ''' Returns an IVCurvePair where only the overlapped and 
        interpolated energies data is included for both curves. 
        
        Returns
        -------
        IVCurvePair : 
            Object containing the overlapping experimental and 
            theoretical IV curves, with the theoretical IV interpolated 
            as necessary.
        
        Notes
        -----
        The theoretical IV data is interpolated so that the 
        energies of both data sets match for easier comparison 
        (using the RFactor)
        '''
        from scipy import interpolate
        
        overlap = deepcopy(self)
        data_overlap = self.data_overlap()
        theory, expt = (data_overlap['theory'], data_overlap['experiment']) 
        tck = interpolate.splrep(theory[0], theory[1], s)
        theory[1] = interpolate.splev(expt[0], tck, der)
        
        overlap.experiment.data = expt
        overlap.theory.data = theory
        
        return overlap
    

class IVCurveGroup(MutableMapping):
    def __init__(self, 
                 group_name=None, 
                 datasets=[], 
                 theta=0., 
                 phi=0., 
                 group_id=0):
        self.theta = theta
        self.phi = phi
        self._datasets = OrderedDict()
        self.datasets = datasets
        self.id = group_id
        self.name = group_name
    
    def __repr__(self):
        module = self.__class__.__module__ 
        module = module if module != '__main__' else None
        if module is None or module == str.__class__.__module__:
            name = self.__class__.__name__
        else:
            name = module + '.' + self.__class__.__name__
        return ("{}(group_name='{}', datasets={}, theta={}, phi={}, "
                "group_id={})".format(name, self.name, self.datasets, 
                                      self.theta, self.phi, self.id))

    def __eq__(self, other):
        return self._datasets == other._datasets
    
    def __ne__(self, other):
        return self._datasets != other._datasets
    
    def __lt__(self, other):
        return len(self.id) < len(other.id)

    def __gt__(self, other):
        return len(self.id) > len(other.id)

    def __le__(self, other):
        return len(self.id) <= len(other.id)

    def __ge__(self, other):
        return len(self.id) >= len(other.id)

    def __contains__(self, key):
        if isinstance(key, str) or isinstance(key, unicode):
            try:
                # search each keys' beams for matching index 
                keys = [index for index in self._datasets.keys()]
                key_str = str(key)
                found = False 
                for index in keys:
                    if key_str in str(index):
                        key = index
                        found = True
                        break
                if not found:
                    raise KeyError()
            except:
                key = eval(key)  # probably just a simple tuple
        elif hasattr(key, 'index'):
            if callable(key.index):
                key = key.index()
            else:
                key = key.index
        return self._datasets.__contains__(key)
    
    def __len__(self):
        return len(self._datasets)
    
    def __delitem__(self, key):
        if isinstance(key, str) or isinstance(key, unicode):
            key = eval(key)
        elif isinstance(key, int):
            key = self._datasets.keys()[key]
        elif hasattr(key, 'index'):
            try:
                if callable(key.index):
                    key = key.index()
                else:
                    key = key.index
            except TypeError:
                pass
        del self._datasets[key]
        
    def __iter__(self):
        return iter(self._datasets)
    
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
        self._datasets[key] = value
    
    def __getitem__(self, key):
        if isinstance(key, str) or isinstance(key, unicode):
            try:
                # search each keys' beams for matching index 
                keys = self._datasets.keys()
                key_str = str(key)
                found = False 
                for index in keys:
                    if key_str in str(index):
                        key = index
                        found = True
                        break
                if not found:
                    raise KeyError
            except:
                key = eval(key)  # probably just a simple tuple
        elif isinstance(key, int):
            key = self._datasets.keys()[key]
        elif isinstance(key, tuple):
            for beam_set in self._datasets.keys():
                if key in beam_set:
                    key = beam_set
        elif hasattr(key, 'index'):
            try:
                if callable(key.index):
                    key = key.index()
                else:
                    key = key.index
            except TypeError:
                pass 
        return self._datasets.__getitem__(key)
    
    def __hash__(self):
        return self._datasets.__hash__()
    
    def clear(self):
        self._datasets.clear()

    def keys(self):
        self._datasets.keys()

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
        return list(set(self.values()))
    
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
        self.clear()
        for iv_pair in iv_pairs:
            if isinstance(iv_pair, IVCurvePair):
                self.__set_item(str(iv_pair.index), iv_pair)
                if (isinstance(iv_pair.index, set) or 
                    isinstance(iv_pair.index, BeamSet)):
                    for index in iv_pair.index: 
                        self.__setitem__(index, iv_pair)        
            elif isinstance(iv_pair,_tuple):
                self.__setitem__(iv_pair, iv_pairs[iv_pair])
    @name.setter
    def name(self, name):
        self._group_name = name or "group_{}".format(self._group_id)
        
    @classmethod
    def load(cls, ctr_file, res_file=None, **group_kwargs):
        lines = []
        try:
            with open(ctr_file, 'r') as f:
                lines = [line.lstrip() for line in f]
        except IOError:
            raise IOError("Failed to read from control file '{}'"
                          "".format(group))

        # read beam information from LEED theoretical result file
        if res_file == None:
            res_file, ext = os.path.splitext(ctr_file)
            if not ext[1:].isdigit():
                res_file += '.res'
            else:
                # handle multiple datasets
                res_file = os.path.splitext(res_file)[0] + '.res' + ext
        
        try:
            theory_beams = IVCurveGroup.read_theory(res_file)
        except IOError:
            theory_beams = {}
        
        ivs = IVCurveGroup(**group_kwargs)
        for line in lines:
            iv = IVCurvePair.from_control_string(line, ctr_file)
            if isinstance(iv, IVCurvePair):
                for beam in iv.index.beams:
                    beam.data = theory_beams[beam.index()]
                iv.theory = iv.index.get_combined_IV()
                iv.theory.path = res_file
                ivs[iv.index] = iv
        return ivs

    @classmethod
    def read_theory(cls, filename):
        with open(filename, 'r') as f:
            lines = [line.lstrip() for line in f if line.lstrip() != '']
        
        beam_info = {}
        data = []
        for line in lines:
            if line.startswith('#bn'):
                n_beams = int(line.split()[1])
            elif line.startswith('#en'):
                en, ei, ef, es, = [eval(val) for val in line.split()[1:5]]
            elif line.startswith('#bi'):
                vars = [eval(var) for var in line.split()[1:]]
                beam_info[tuple(vars[1:3])] = (vars[0], vars[3])
            elif line.startswith('#'):
                continue  # skip general comment
            else:
                data.append([eval(var) for var in line.split()])
        
        from numpy import loadtxt
        data = loadtxt(filename, dtype=float).transpose()
        x, data = data[0], data[1:]
        if len(data) != n_beams:
            f = lambda x,y: len(x) == len(y)
            if not all(f(y[i], y[i+1]) for i in range(len(data)-1)):
                raise ValueError("LEED theory data has different "
                                 "numbers of datapoints")
        
        for beam in beam_info:
            i, j = beam_info[beam]
            beam_info[beam] = (x, data[i])
        
        return beam_info

    def write(self, ctr_file, res_file):
        from numpy import transpose
        
        with open(ctr_file, 'w') as f:
            f.write("{comments}\n".format(comments='# write test'))
            for dataset in self.datasets:
                for beam in dataset.index:
                    # write individual beam data
                    f.write("{line}\n",
                            str(beam) + '\n')
                 
            
    @property
    def rfactor(self):
        rf = 0.

if __name__ == '__main__':
    filename = os.path.expandvars("%Dropbox%"
                "\\LEED_programs\\CLEED\\CLEED_DIS_1309_safe-mod-mgjf\\EXAMPLES\\NIO\\Ni111_2x2O.res")
    iv_group = IVCurveGroup.load(os.path.expandvars("%Dropbox%"
                            "\\LEED_programs\\CLEED\\CLEED_DIS_1309\\"
                            "EXAMPLES\\NIO\\Ni111_2x2O.ctr"))
    print(iv_group)
    