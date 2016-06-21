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
** model.py ** - Python module for dealing with CLEED models. 
'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

import os
import phaseshifts.model

from phaseshifts.elements import ELEMENTS
from symmetry import RotationalSymmetry, MirrorPlane

from abc import ABCMeta
from copy import deepcopy
from collections import OrderedDict, Sequence

class Atom(phaseshifts.model.Atom):
    def __init__(self, *args, **kwargs):
        self.dr = kwargs.pop('dr', [0.025])
        phaseshifts.model.Atom.__init__(self, *args, **kwargs)
    
    def __str__(self):
        args = [self.tag]
        args += self.coordinates
        args += self.dr
        if len(self.dr) is 3:
            return ('{} {:10.6f} {:4.6f} {:4.6f}  dr3  {:5.3f} {:5.3f} {:5.3f}'
                    ''.format(*args))
        elif len(self.dr) is 1:
            return ('{} {:10.6f} {:10.6f} {:10.6f}  dr1  {:5.3f}'.format(*args))
        
    @property
    def dr(self):
        return self._dr
    
    @dr.setter
    def dr(self, dr):
        if len(dr) is 1:
            self._dr = [float(x) for x in dr[:1]]
        elif len(dr) is 3:
            self._dr = [float(x) for x in dr[:3]]
        else:
            raise TypeError('dr must be array-like of length 1 or 3')

class UnitCell(phaseshifts.model.Unitcell):
    def __init__(self, a=1., c=1., 
                 matrix3x3=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], 
                 *args, **kwargs):
        super(UnitCell, self).__init__(a, c, matrix3x3, *args, **kwargs)
    
    def __str__(self, *args, **kwargs):  
        return ('# unitcell:\n'
                'a1: {:.6f} {:.6f} {:.6f}\n'
                'a2: {:.6f} {:.6f} {:.6f}\n'
                'a3: {:.6f} {:.6f} {:.6f}\n'
                ''.format(list(self.basis[0] + self.basis[1] + self.basis[2])))

class SuperStructure(UnitCell):
    STRUCTURES = OrderedDict([('p(1x1)', ((1., 0.), (0., 1.))),
                              ('p(1x2)', ((1., 0.), (0., 2.))),
                              ('p(2x1)', ((2., 0.), (0., 1.))),
                              ('p(2x2)', ((2., 0.), (0., 2.))),
                              ('p(3x1)', ((3., 0.), (0., 1.))),
                              ('p(3x2)', ((3., 0.), (0., 2.))),
                              ('p(3x2)', ((3., 0.), (0., 3.))),
                              ('p(7x7)', ((7., 0.), (0., 7.))),
                              ('c(2x2)', ((1., -1.), (1., 1.))),
                              ('c(4x2)-square', ((2., -1.), (2., 1.))),
                              ('c(4x2)-hexagonal', ((2., 1.), (0., 2.))),
                              ('c(4x4)', ((2., -2.), (2., 2.))),
                              ('c(6x2)', ((3., -1.), (3., 1.))),
                              ('c(8x2)', ((4., -1.), (4., 1.))),
                              ('(r2xr2)R45-square', ((1., -1.), (1., 1.))),
                              ('(r5xr5)R26.6-square', ((2., 1.), (-1., 2.))),
                              ('(2r2xr2)R45-square', ((2., 2.), (-1., 1.))),
                              ('c(3r2xr2)R45-square', ((2., 1.), (1., 2.))),
                              ('c(5r2xr2)R45-square', ((3., 2.), (2., 3.))),
                              ('(r3xr3)R30-hex', ((1., -1.), (1., 2.))),
                              ('(r7xr7)R19.1-hex', ((2., -1.), (1., 3.))),
                              ('(2r3x2r3)R30-hex', ((2., -2.), (2., 4.))),
                              ('(2r3x4)rect-hex', ((4., 0.), (2., 4.))),
                              ('(5r3x2)rect-hex', ((2., 2.), (-5., 5.))),
                              ('c(2r3x4)rect-hex', ((3., 1.), (1., 3.)))])
    
    def __init__(self, 
                 a=0, c=0, super_matrix=[[1., 0.], [0., 1.]], 
                 *args, **kwargs):
        UnitCell.__init__(self, a, c, *args, **kwargs)
        self.M = super_matrix
        if 'basis' in kwargs:
            self.basis = kwargs['basis']
        else:
            self.basis = [[1., 0.], [0., 1.]]
        self._c = None
        self._gamma = None
    
    @property
    def gamma(self):
        return UnitCell.gamma(self)
        
    @gamma.setter
    def gamma(self, gamma):
        self._gamma = None
    
    @property
    def c(self):
        return self._c
    
    @c.setter
    def c(self, c):
        self._c = None
        
    @property
    def basis(self):
        return self._basis
    
    @basis.setter
    def basis(self, basis):
        try:
            self._basis = [bas[:2] for bas in basis[:2]]
        except IndexError:
            IndexError('basis must be 2x2 or 3x3 matrix')

    def __str__(self, *args, **kwargs):
        return ('# supercell:\n'
                'a1: {}\n'
                'a2: {}\n'
                '\n'
                '# superstructure matrix:\n'
                'm1: {} {}\n'
                'm2: {} {}\n'
                ''.format(' '.join([':.6f'.format(a) for a in self.basis[0]]),
                          ' '.join([':.6f'.format(a) for a in self.basis[1]]),
                          self.m11, self.m12, self.m21, self.m22))
    
    def __repr__(self):
        return ("SuperStructure(super_matrix={}, a={}, b={},"
                "alpha={}, beta={}, basis={})"
                "".format(self.M, self.a, self.b, 
                          self.alpha, self.beta, 
                          [b[:2] for b in self.basis[:2]]))
    
    @property
    def M(self):
        return self._superstructure_matrix
    
    @property
    def m11(self):
        return self.M[0][0]
    
    @property
    def m12(self):
        return self.M[0][1]
    
    @property
    def m21(self):
        return self.M[1][0]
    
    @property
    def m22(self):
        return self.M[1][1]    

    @M.setter
    def M(self, matrix):
        if isinstance(matrix, str):
            self._superstructure_matrix = self.STRUCTURES[matrix]
        else:
            try:
                import numpy as np
                matrix = np.array(matrix)
                if np.shape(matrix) > (2, 2):
                    matrix = matrix[:2][:2]
                elif np.shape(matrix) < (2, 2):
                    raise IndexError('matrix must be 2x2')
            except ImportError:
                if len(matrix) is 2 and len(matrix[0]) is 2 and len(matrix[1]) is 2:
                    matrix = matrix[:2][:2]
                else:
                    raise IndexError('matrix must be 2x2')
            finally:
                self._superstructure_matrix = matrix
    
    @m11.setter
    def m11(self, m11):
        self._superstructure_matrix[0][0] = m11
    
    @m12.setter
    def m12(self, m12):
        self._superstructure_matrix[0][1] = m12
    
    @m21.setter
    def m21(self, m21):
        self._superstructure_matrix[1][0] = m21
    
    @m22.setter
    def m22(self, m22):
        self._superstructure_matrix[1][1] = m22


class BaseModel(phaseshifts.model.Model):
    '''Base class for CLEED models'''
    
    COMMANDS = ['c']
    
    def export_xyz(self, xyz_file, comment_line=''):
        comment_line = comment_line if comment_line is not '' else xyz_file
        try:
            with open(xyz_file, 'w') as xyz:
                xyz.write('{}\n'.format(len(set(self.atoms))))
                xyz.write('#{}\n'.format(comment_line))
                xyz.write('\n'.join(['{} {} {}'.format(*atom.coordinates) 
                                     for atom in set(self.atoms)]))
            return True
        except any as e:
            raise e
    
    @classmethod
    def load(cls, filename):
        raise NotImplementedError
        
    def save(self, filename):
        raise NotImplementedError
    
    @property
    def comment(self):
        return self._comment
    
    @comment.setter
    def comment(self, comment):
        self._comment = comment
    
    @staticmethod
    def eval_line(line):
        '''
        Evaluates input line
        '''
        cmd, vars = line.split(':')
        cmd = cmd.lstrip()
        if cmd in ['a1', 'a2', 'a3']:
            return [float(z) for z in vars[:3]]
        elif cmd in ['m1', 'm2']:
            return [float(m) for m in vars[:2]]
        elif cmd is 'zr':
            return [float(z) for z in vars[:2]]
        elif cmd is 'sr':
            return [t(s) for t, s in zip((int, float, float), vars[:3])] 
        elif cmd is 'sz':
            return int(vars[0])
        elif cmd in ['po', 'pb']:
            try:
                idr = vars.index('dr1')
                ndr = idr+1
            except:
                idr = vars.index('dr3')
                ndr = idr+3
            
            return Atom(vars[0].split('_')[0], 
                        tag=vars[0], 
                        coordinates=[float(coord) for coord in vars[1:4]], 
                        dr=[float(dw) for dw in vars[idr:ndr]])
        elif cmd in ['vr', 'vi']:
            return float(vars[0])
        elif cmd in ['ei', 'ef', 'es']:
            return float(vars[0])
        elif cmd.startswith('ip') or cmd.startswith('it'):
            return float(vars[0])
        elif cmd is 'ep':
            return float(vars[0])
        elif cmd is 'lm':
            return int(vars[0])
        elif cmd is 'rm':
            return [t(s) for t, s in zip((str, float), vars[:2])]
        elif cmd in ['il', 'nl']:
            return int(vars[0])
        else:
            return None
    
    @staticmethod
    def eval(filename):
        cmds_dict = {}
        with open(filename, 'r') as f:
            for line in f:
                line = line.lstrip()
                if ':' in line:
                    cmd, args = line.split(':')
                    if len(cmd):
                        if cmd == 'c':
                            pass 
                        elif not cmd.startswith('p'):
                            cmds_dict[cmd] = tuple([eval(var) for var 
                                                    in args.split()])
                        else:
                            vars = args.split()
                            try:
                                idr = vars.index('dr1') + 1
                                ndr = idr
                            except ValueError:
                                idr = vars.index('dr3') + 1
                                ndr = idr+3
                            
                            if cmd not in cmds_dict:
                                cmds_dict[cmd] = []
                            cmds_dict[cmd] += [Atom(vars[0].split('_')[0], 
                                                   tag=vars[0], 
                                                   coordinates=[float(x) for x 
                                                                in vars[1:4]], 
                                                   dr=[float(dw) for dw 
                                                       in vars[idr:ndr]]
                                                   )
                                               ]
            return cmds_dict
                    
    
class BulkModel(BaseModel):
    '''Class for specifying CLEED bulk structure'''
    
    COMMANDS = BaseModel.COMMANDS + ['a1', 'a2', 'a3', 'm1', 'm2']
    
    @classmethod
    def load(cls, filename):
        kwargs = BulkModel.eval(filename)
        bulk_model = BulkModel()
        
        uc = UnitCell(a=kwargs.pop('a1'), 
                      b=kwargs.pop('a2'),
                      c=kwargs.pop('a3'),
                      coordinates=kwargs.pop())

    def save(self, filename, extra_cmds={}):
        ''' Saves BulkModel instance to `filename`
        
        Parameters
        ----------
        filename : str
            Path to desired output file.
        extra_cmds : dict
            Dictionary of additional command variables to include in the 
            output file.
            
        '''
        try:
            with open(filename, 'w') as f:
                f.write('# CLEED bulk model - {}\n'
                        'c: {comment}\n'
                        '{unitcell}\n\n'
                        '{atoms}\n\n'
                        ''.format(filename, 
                                  comment=self.comment,
                                  unitcell=str(self.unitcell),
                                  atoms='\n'.join([str(atom) for atom 
                                                   in self.atoms]) 
                                  )
                        )
                if extra_cmds is not {}: 
                    f.write('\n# other:\n')
                    for cmd in extra_cmds:
                        if isinstance(extra_cmds[cmd], Sequence):
                            var_str = ' '.join([var for var in extra_cmds[cmd]])
                            f.write('{}: {}'.format(cmd, var_str))
                        else:
                            f.write('{}: {}'.format(cmd, extra_cmds[cmd]))
        except IOError as err:
            raise err
    
    @staticmethod
    def eval_line(line):
        line = line.lstrip()
        cmd = line.split(':')[0]
        if cmd in self.COMMANDS:
            return BaseModel.eval_line(line)



class SurfaceModel(BaseModel):
    '''Class for specifying CLEED surface structure'''
    def __init__(self, rot_sym=None, mirror_plane=None, *args, **kwargs):
        BaseModel.__init__(self, *args, **kwargs)
        self.rotational_symmetry = rot_sym
        self.mirror_plane = mirror_plane
    
    @property
    def z_range(self):
        return self._zr
    
    @z_range.setter
    def z_range(self):
        raise NotImplementedError
    
    @property
    def z_only(self):
        return int(self._sz)
    
    @z_only.setter
    def z_only(self, sz):
        self._sz = bool(sz)
    
    @property
    def superstructure(self):
        return self.unitcell.M
    
    @property
    def rotational_symmetry(self):
        return self._sr
    
    @property
    def mirror_plane(self):
        return self._sm

    @rotational_symmetry.setter
    def rotational_symmetry(self, rot_sym):
        if isinstance(rot_sym, RotationalSymmetry):
            self._sr = rot_sym
    
    @mirror_plane.setter
    def mirror_plane(self, mirror_plane):
        if isinstance(mirror_plane, MirrorPlane):
            self._sm = mirror_plane
    
    def load(self, filename):
        lines = []
        with open(filename, 'r') as f:
            lines = [line.lstrip() for line in f]
        
        atoms = [self._eval_po for po in lines if po.startswith('po:')]
        unitcell = UnitCell()
        superstructure = SuperStructure()
        comments = ' '.join([c for c in lines if c.startswith('c:')])

class Model(BaseModel):
    def __init__(self, bulk, surface):
        self.bulk_model = bulk
        self.surface_model = surface
    
    @property
    def bulk_model(self):
        return self._bulk
    
    @property
    def surface_model(self):
        return self._surface
    
    @property
    def atoms(self):
        return self.bulk_model.atoms + self.surface_model.atoms 
    
    @bulk_model.setter
    def bulk_model(self, model):
        if isinstance(model, BulkModel):
            self._bulk = deepcopy(model)
        else:
            raise TypeError('bulk model must be of type BulkModel') 
    
    @surface_model.setter
    def surface_model(self, model):
        if isinstance(model, BulkModel):
            self._bulk = deepcopy(model)
        else:
            raise TypeError('surface model must be of type SurfaceModel')


def inp2xyz(filename, xyz_filename=None):
    atoms = []
    xyz_filename = xyz_filename or os.path.splitext(filename)[0] + '.xyz'
    try:
        with open(filename, 'r') as f:
            lines = [line for line in f]
   
    except IOError:
        assert IOError("***error (inp2xyz): Could not open file '%s'" 
                       % filename)
       
    for line in lines:
        if (line.lstrip().startswith('po:') or 
            line.lstrip().startswith('pb:')):
            line = line.lstrip()[3:].lstrip()
            element, x, y, z, = [t(s) for (t, s) in 
                                 zip((str, float, float, float),
                                 line.split()[0:5])]
            element = element.split('_')[0]
            try:
                if element in ELEMENTS:
                    atoms.append("%s %9.6f %9.6f %9.6f" 
                                 % (ELEMENTS[element].symbol, x, y, z))
            except KeyError:
                pass

    try:
        with open(xyz_filename, 'w') as f:
            f.write("%i \n" % len(atoms))
            f.write("#jmolscript: select *;"
                    "color bonds lightgrey;"
                    "background white;"
                    "set antialiasdisplay true;"
                    "set perspectiveDepth false;"
                    "set cameraDepth 10;"
                    "set diffusePercent 85;"
                    "boundboxColor = \"[xa9a9a9]\";"
                    "set ambientPercent 60;"
                    "set diffusePercent 85;"
                    "set specular true;"
                    "set specularPercent 22;"
                    "set specularPower 40;"
                    "set specularExponent 6;"
                    "set zShadePower 3;"
                    "\n")
            for atom in atoms:
                f.write(atom + '\n')
            
    except IOError:
        raise IOError("***error (inp2xyz): Could not write file '%s'" 
                      % xyz_filename)

if __name__ == '__main__':
    b = BaseModel(atoms=[])
    res = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'res'))
    filename = os.path.join(res, 'examples', 'models', 'nio', 'Ni111_2x2O.bul')
    b = BulkModel(atoms=[])
    print(str(b))
    print(BaseModel.eval(filename))
    