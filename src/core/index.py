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
**index.py** - module for dealing with Miller indices
'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

class MillerIndex(object):
    def __init__(self, h, k, l=None):
        self.h = h
        self.k = k
        self.l = l
    
    def __eq__(self, other):
        return (self.h == other.h and 
                self.k == other.k and
                self.l == other.l)
    
    def __ne__(self, other):
        return not (self.h == other.h and 
                    self.k == other.k and
                    self.l == other.l)
    
    def __gt__(self, other):
        return self.order() > other.order()

    def __ge__(self, other):
        return self.order() >= other.order()
    
    def __lt__(self, other):
        return self.order() < other.order()

    def __le__(self, other):
        return self.order() <= other.order()
    
    def __str__(self):
        if not self.l:
            return '({h:.3f}, {k:.3f})'.format(h=self.h, 
                                               k=self.k)
        else:
            return '({h:.3f}, {k:.3f}, {l:.3f})'.format(h=self.h, 
                                                        k=self.k, 
                                                        l=self.l)
    
    def __repr__(self):
        if not self.l:
            return 'MillerIndex({h:.3f}, {k:.3f})'.format(h=self.h, k=self.k)
        else:
            return 'MillerIndex({h:.3f}, {k:.3f}, {l:.3f})'.format(h=self.h, 
                                                                   k=self.k, 
                                                                   l=self.l)
    
    def __hash__(self):
        return hash(self.__repr__())
    
    @property
    def h(self):
        return self._miller_h
    
    @property
    def k(self):
        return self._miller_k
    
    @property
    def l(self):
        return self._miller_l
    
    @h.setter
    def h(self, h):
        self._miller_h = float(h)
        
    @k.setter
    def k(self, k):
        self._miller_k = float(k)
        
    @l.setter
    def l(self, l):
        if l is not None:
            self._miller_l = float(l)
        else:
            self._miller_l = None
            
    def index(self):
        ''' Returns the Miller indices as a tuple '''
        return eval(self.__str__())
    
    def order(self, round=False):
        ''' Returns the order of the diffraction spot '''
        f = lambda x: int(x) if round else x
        return f(abs(self.h) + abs(self.k))


class MillerDirection(MillerIndex):
    def __str__(self):
        MillerIndex.__str__().replace('(', '[').replace(')', ']')

        
class MillerPlane(MillerIndex):
    def __repr__(self):
        pass


class MillerIndexSet(object):
    '''
    Convenience class for handling MillerIndex lists 
    '''
    def __init__(self, indices=[]):
        self.indices = indices
        
    def __str__(self):
        return '+'.join([str(index) for index in set(self.indices) 
                         if isinstance(index, MillerIndex)])

    @property
    def indices(self):
        return set(self._indices)
    
    @indices.setter
    def indices(self, indices):
        values = []
        for ind in indices:
            if isinstance(ind, str):
                index = eval(ind)
            elif isinstance(ind, MillerIndex):
                pass
            else:
                index = MillerIndex(*ind)
            values.append(index)
        self._indices = values

if __name__ == '__main__':
    miller = MillerIndex(0., 0.5)
    miller2 = MillerIndex(0., 0.5, 0.1)
    print(set([miller, miller2]))
    