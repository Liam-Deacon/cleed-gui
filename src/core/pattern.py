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
**pattern.py** - defines basic classes for LEED pattern simulation
'''
from __future__ import division, with_statement, unicode_literals

from model import UnitCell, SuperStructure
from index import MillerIndex

from math import cos, sin, pi, sqrt 
import numpy as np

class Spot(MillerIndex):
    '''
    Class for defining a LEED spot
    '''
    def __init__(self, x, y, h, k):
        MillerIndex.__init__(self, h, k)
        self.x = x
        self.y = y
    
    def __repr__(self):
        return ('Spot(x={}, y={}, h={:.4f}, k={:.4f})'
                ''.format(self.x, self.y, self.h, self.k))
    
    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y
    
    @x.setter
    def x(self, x):
        self._x = float(x)
    
    @y.setter
    def y(self, y):
        self._y = float(y)
        
    def pos(self):
        return (self._x, self._y)


class Domain(SuperStructure):
    def __init__(self, matrix=np.identity(2, dtype=float), 
                 pattern=None, matrix_op=None, radius=1.):
        SuperStructure.__init__(self, super_matrix=matrix)
        self.pattern = pattern
        if isinstance(pattern, UnitCell):
            self.a = pattern.a
            self.b = pattern.b
            self.basis = pattern.basis
            self.alpha = pattern.alpha
            self.beta = pattern.beta
            
        if hasattr(pattern, 'radius'):
            self.radius = pattern.radius
        else:
            self.radius = radius
            
        if matrix_op is not None:
            self.do_operation(matrix_op)
    
    def __str__(self):
        return '{} {}\n{} {}'.format(*','.join(['{:7.4f}'.format(a) for a 
                                in np.array(self.M).flatten()]).split(','))
    
    def __repr__(self):
        return ('Domain(matrix=[[{:9.6f}, {:9.6f}][{:9.6f}, {:9.6f}]])'
                ''.format(self.m11, self.m12, self.m21, self.m22)) 

    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, radius):
        self._radius = float(radius) 

    @property
    def commensurate(self):
        return (not ((abs(self.m11) - int(abs(self.m11) + 0.1) > 0.05) or
                     (abs(self.m12) - int(abs(self.m12) + 0.1) > 0.05) or 
                     (abs(self.m21) - int(abs(self.m21) + 0.1) > 0.05) or 
                     (abs(self.m22) - int(abs(self.m22) + 0.1) > 0.05) ) )

    def do_operation(self, op):
        op = op.lstrip().split('#')[0].rstrip().lower()
        value = float(op[1:])
        M11, M12, M21, M22 = list(self.M[0] + self.M[1])
        m11, m12, m21, m22 = list(self.M[0] + self.M[1])
        if op[0] == 'r':
            det = a1[0]*a2[1] - a1[1]*a2[0]
            aux2 = (a1[0]*a2[0] + a1[1]*a2[1]) / det

            N11 =  cos(phi) - aux2*sin(phi)
            N12 =  sin(phi) * (a1[0]*a1[0] + a1[1]*a1[1]) / det
            N21 = -sin(phi) * (a2[0]*a2[0] + a2[1]*a2[1]) / det
            N22 =  cos(phi) + aux2*sin(phi)
    
            m11 = M11*N11 + M12*N21
            m12 = M11*N12 + M12*N22
            m21 = M21*N11 + M22*N21
            m22 = M21*N12 + M22*N22
    
            M11 = m11 
            M12 = m12 
            M21 = m21 
            M22 = m22

        elif op[0] == 's':
            det = a1[0]*a2[1] - a1[1]*a2[0]
            aux2 = (a1[0]*a2[1] + a1[1]*a2[0]) / det

            if line[1] == 'x':
                N11 = aux2
                N12 = -2 * a1[0]*a1[1] / det
                N21 =  2 * a2[0]*a2[1] / det
                N22 = -aux2
            elif line[1] == 'y':
                N11 = -aux2
                N12 =  2 * a1[0]*a1[1] / det
                N21 = -2 * a2[0]*a2[1] / det
                N22 = aux2
            else:
                raise ValueError("Symmetry operation must be either 'x' or 'y'")

            m11 = M11*N11 + M12*N21
            m12 = M11*N12 + M12*N22
            m21 = M21*N11 + M22*N21
            m22 = M21*N12 + M22*N22

            M11 = m11 
            M12 = m12 
            M21 = m21 
            M22 = m22
        else:
            ValueError("Operation is not recognised - use either 'R' or 'S'")
        
        self.M = [[m11, m12], [m21, m22]]    
        
        return self.M
    
    def calculate_spots(self, r_max=10.):
        pat = self
        spots = []
        
        radius = self.radius
        
        # scale spot sizes by radius 
        if (pat.basis[0][0]*pat.basis[0][0] + pat.basis[0][1]*pat.basis[0][1] > 
            pat.basis[1][0]*pat.basis[1][0] + pat.basis[1][1]*pat.basis[0][1]):
            radius *= sqrt(pat.basis[0][0]*pat.basis[0][0] + 
                           pat.basis[0][1]*pat.basis[0][1])
        else:
            radius *= sqrt(pat.basis[1][0]*pat.basis[1][0] + 
                           pat.basis[1][1]*pat.basis[1][1])
  
        radius = r_max / radius

        # calculate GS vectors
        a1 = (radius*pat.basis[1][1], -radius*pat.basis[1][0])
        a2 = (-radius*pat.basis[0][1], radius*pat.basis[0][0])
        
        # define max. values */
        h_max = 5 * int( r_max / sqrt(a1[0]*a1[0] + a1[1]*a1[1]) )
        k_max = 5 * int( r_max / sqrt(a2[0]*a2[0] + a2[1]*a2[1]) )
        
        # SUPERSTRUCTURE SPOTS
           
        # set local superstructure matrix elements
        m11, m12, m21, m22 = np.array(self.M).flatten()
        
        # determinant of matrix
        det  = m11*m22 - m12*m21
        aux1 = 1./det
        det = abs(det)
        
        # calculate SS vectors 
        b1 = (aux1 *(m22*a1[0] - m21*a2[0]), aux1 *(m22*a1[1] - m21*a2[1]))
        b2 = (aux1 *(m11*a2[0] - m12*a1[0]), aux1 *(m11*a2[1] - m12*a1[1]))
           
        # define max. values 
        smax_1 = 5 * int(r_max / sqrt(b1[0]*b1[0] + b1[1]*b1[1]))
        smax_2 = 5 * int(r_max / sqrt(b2[0]*b2[0] + b2[1]*b2[1]))
        
        # determine number of spots */
        if self.commensurate:
            for s1 in range(-smax_1, smax_1):
                for s2 in range(-smax_2, smax_2):
                    x, y = (s1*b1[0] + s2*b2[0], s1*b1[1] + s2*b2[1])
                    h, k = (s1*m22 - s2*m12, s2*m11 - s1*m21)
                    if (x*x + y*y) <= r_max**2: 
                      spots.append(Spot(x, y, h, k))
             
        else:
            # If the Mii are not integer, the superstructure is incommensurate.
            # In this case the multiple scattering spots must be calculated
            # separately.

            # add multiple scattering SS spots to list */
            for h in range(-h_max, h_max+1):
              for k in range(-k_max, k_max+1):
                  if h != 0 or k != 0:
                      xi = h*a1[0] + k*a2[0]
                      yi = h*a1[1] + k*a2[1]
                  
                  if (xi*xi + yi*yi) <= r_max: 
                    for s1 in range(-smax_1, smax_1):
                      for s2 in range(-smax_2, smax_2):
                          x = xi + s1*b1[0] + s2*b2[0]
                          y = yi + s1*b1[1] + s2*b2[1]
                      
                          if (x*x + y*y) <= r_max**2 and (s1 != 0 or s2 != 0):
                              spots.append(Spot(x, y, h, k))
        return spots


class Pattern(Domain):
    def __init__(self, domains=[], radius=1., *args, **kwargs):
        kwargs['radius'] = radius
        Domain.__init__(self, *args, **kwargs)
        self.domains = domains
    
    def __str__(self):
        return ('# Pattern:\n'
                '{}\n'
                '{:8.4f} {:8.4f} a1\n'
                '{:8.4f} {:8.4f} a2\n'
                '{:g} radius\n'
                '{} domains\n'
                '# Substrate matrix: \n'
                '{:7.4f} {:7.4f} M1\n'
                '{:7.4f} {:7.4f} M1\n'
                '# Superstructure domains:\n'
                '{}\n'
                ''.format('\n'.join(['c' + line for line 
                                     in self.title.split('\n') if line != '']),  
                          self.basis[0][0], self.basis[0][1], 
                          self.basis[1][0], self.basis[1][1],
                          self.radius,
                          len(self.domains),
                          self.M[0][0], self.M[0][1],
                          self.M[1][0], self.M[1][1],
                          '\n'.join(['{} D{}'.format(dom, i) for i, dom 
                                     in enumerate(self.domains)])
                          )
                )
    
    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, title):
        self._title = str(title)
        
    @property
    def basis(self):
        return UnitCell.basis
    
    @basis.setter
    def basis(self, basis):
        UnitCell.basis = basis
    
    @property
    def domains(self):
        return self._domains
    
    @domains.setter
    def domains(self, domains):
        self._domains = [dom for dom in domains if isinstance(dom, Domain)]
    
    def add_domain(self, domain):
        if isinstance(domain, Domain):
            self._domains.append(domain)
        return self
            
    def pop_domain(self, domain):
        if isinstance(domain, int):
            return self._domains.pop(domain)
        elif isinstance(domain, Domain):
            return self._domains.pop(self._domains.index(domain))
    
    @classmethod
    def read(cls, filename):
        '''
        Returns a :class:`Pattern` instance read from file
        
        Parameters
        ----------
        filename : str
            Path to read from.
            
        Returns
        -------
        :class:`Pattern` :
            New LEED pattern instance.
        '''
        lines = []
        with open(filename, 'r') as f:
            lines = [line.split('#')[0].lstrip().rstrip() for line in f 
                     if not line.lstrip().startswith('#') and line != '']
  
        pat = Pattern()
  
        comments = ''
        for comment in (ln for ln in lines if ln.startswith('c')):
            comments += '{}\n'.format(lines.pop(lines.index(comment)).split('c')[1].replace(':', '').lstrip())
            
        pat.title = comments
  
        # substrate structure
        a1 = [t(s) for t, s in zip((float, float), lines.pop(0).split()[0:2])]
        a2 = [t(s) for t, s in zip((float, float), lines.pop(0).split()[0:2])]
        pat.basis = [a1, a2]
  
        # calculate max length in k-space (radius is the max. k-distance in
        # units of the longest rec. lattice vector) 
        # rescale spot size
        pat.radius = float(lines.pop(0).split()[0])

        # Domains   
        n_domains = abs(int(lines.pop(0).split()[0]))
        M11, M12, M21, M22 = (1., 0., 0., 1.)
        for i in range(n_domains):
            line = lines.pop(0).lower()
            if line.startswith('r'):
                try:
                    phi = float(line[1:]) * pi / 180.
                except ValueError:
                    raise ValueError('Rotation angle must be a valid number')
                    continue
                det = a1[0]*a2[1] - a1[1]*a2[0]
                aux2 = (a1[0]*a2[0] + a1[1]*a2[1]) / det

                N11 =  cos(phi) - aux2*sin(phi)
                N12 =  sin(phi) * (a1[0]*a1[0] + a1[1]*a1[1]) / det
                N21 = -sin(phi) * (a2[0]*a2[0] + a2[1]*a2[1]) / det
                N22 =  cos(phi) + aux2*sin(phi)
        
                m11 = M11*N11 + M12*N21
                m12 = M11*N12 + M12*N22
                m21 = M21*N11 + M22*N21
                m22 = M21*N12 + M22*N22
        
                M11 = m11 
                M12 = m12 
                M21 = m21 
                M22 = m22

            elif line.startswith('s'):
                det = a1[0]*a2[1] - a1[1]*a2[0]
                aux2 = (a1[0]*a2[1] + a1[1]*a2[0]) / det

                if line[1] == 'x':
                    N11 = aux2
                    N12 = -2 * a1[0]*a1[1] / det
                    N21 =  2 * a2[0]*a2[1] / det
                    N22 = -aux2
                elif line[1] == 'y':
                    N11 = -aux2
                    N12 =  2 * a1[0]*a1[1] / det
                    N21 = -2 * a2[0]*a2[1] / det
                    N22 = aux2
                else:
                    raise ValueError("Symmetry operation must be either 'x' or 'y'")
                    continue

                m11 = M11*N11 + M12*N21
                m12 = M11*N12 + M12*N22
                m21 = M21*N11 + M22*N21
                m22 = M21*N12 + M22*N22

                M11 = m11 
                M12 = m12 
                M21 = m21 
                M22 = m22

            else:
                try:
                    M11, M12 = [float(m) for m in line.split()[:2]]
                    M21, M22 = [float(m) for m in lines.pop(0).split()[:2]]
                except ValueError:
                    raise ValueError('a1 and a2 must contain valid numbers')
                    continue
                except IndexError:
                    raise IndexError('a1 and a2 must have 2 components')

                m11 = M11
                m12 = M12
                m21 = M21
                m22 = M22
                        
                N11 = N22 = 1. 
                N12 = N21 = 0.
                
            # add superstructure matrix
            pat.domains.append(Domain(matrix=[[m11, m12], [m21, m22]], 
                                      pattern=pat))
            if len(lines) == 0:
                break
  
        return pat
    
    def calculate_spots(self, r_max=10.):
        spots = []
        pat = self
        
        radius = self.radius
        
        # scale spot sizes by radius 
        if (pat.basis[0][0]*pat.basis[0][0] + pat.basis[0][1]*pat.basis[0][1] > 
            pat.basis[1][0]*pat.basis[1][0] + pat.basis[1][1]*pat.basis[0][1]):
            radius *= sqrt(pat.basis[0][0]*pat.basis[0][0] + 
                           pat.basis[0][1]*pat.basis[0][1])
        else:
            radius *= sqrt(pat.basis[1][0]*pat.basis[1][0] + 
                           pat.basis[1][1]*pat.basis[1][1])
  
        radius = r_max / radius

        # calculate GS vectors
        a1 = (radius*pat.basis[1][1], -radius*pat.basis[1][0])
        a2 = (-radius*pat.basis[0][1], radius*pat.basis[0][0])
     
        # define max. values
        h_max = 5 * (int)( r_max / sqrt(a1[0]*a1[0] + a1[1]*a1[1]) )
        k_max = 5 * (int)( r_max / sqrt(a2[0]*a2[0] + a2[1]*a2[1]) )
      
        # calculate substrate spots
        for h in range(-h_max, h_max+1):
            for k in range(-k_max, k_max+1):
              xi = h * a1[0] + k * a2[0]
              yi = h * a1[1] + k * a2[1]
              if (xi*xi + yi*yi) <= r_max**2:
                  spots.append(Spot(xi, yi, h, k))
  
        return spots


def is_fraction(numerator, denominator):
    ''' Makes nicer fractions '''
    if numerator == 0:
        return numerator, denominator

    if denominator < 0:
        number = -denominator/2;
    else:
        number = denominator/2;

    ggt = 1
    for i in range(2, number+1):
        if (numerator % i == 0) and (denominator % i == 0): 
            ggt = i
            break

    numerator /= ggt
    denominator /= ggt

    if numerator % denominator == 0:
        numerator /= denominator
    
    return numerator, denominator
    
if __name__ == '__main__':
    filename = r"C:\\Users\\kss07698\\Dropbox\\Windows Tweaks\\CLEED_tools_win32\\cleed\\src\\CLEED\\examples\\patt\\bcc100.2x1_1.patt"
    patt = Pattern.read(filename)
    print('pattern = ', patt)
    print('\n'.join([repr(spot) for spot in patt.calculate_spots() if spot.index() == (0, 0)]))
