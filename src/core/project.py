##############################################################################
# Author: Liam Deacon                                                        #
#                                                                            #
# Contact: liam.m.deacon@gmail.com                                           #
#                                                                            #
# Created on 23 Jun 2014                                                     #
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
*project.py* - module for controlling CLEED projects.
'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

import os.path
from environ import Environment

class Project(object):
    ''' 
    Class for storing project details pertaining to a given CLEED model.
    
    Attributes
    ----------
    name : str
        Name of the model. This is also the name of the working directory in 
        addition to the file prefix for all related files.
    model_root : str
        Filepath to parent directory. The default is `~/CLEED`.
    bulk_model : BulkModel
        Bulk model.
    surface_model : SurfaceModel
        Surface model.
    control : Control
        Handle for Control class instance governing interaction between 
        theoretical and experimental IV curves.
    search : Search
        Object handle for controlling a minimisation search of the model 
        geometry.
    rfactor : RFactor
        Handle for R-Factor calculations. 
    IV_curves : dict
        Dictionary of theoretical and experimental IV curve lists.
    environment : Environment
        Options relevant to the CLEED setup including environment variables and 
        executable paths.
    Methods
    -------
    import_project(path)
        Imports a model from an existing set of *.inp, *.bul and *.ctr files. 
    save(path)
        Saves project to disk.
    load(path)
        Loads a project configuration file from disk.
    clone(new_path, new_name="")
        Copies project and appropriately renaming all files.
    '''
    
    def __init__(self, name, root_dir="", **kwargs):
        self.model_name = name
        self.model_root = root_dir
        self.IV_curves = {'expt': [], 'theory': []}
        dir = os.path.join(self.model_root, self.model_name)
        base = os.path.join(dir, self.model_name) 
        
        if os.path.exists(base + '.cfg'):
            self.load(base + '.cfg')
        elif (os.path.exists(base + '.inp') and 
              os.path.exists(base + '.bul') and 
              os.path.exists(base + '.ctr')):
            self.import_project(dir)
    
    @property
    def model_name(self):
        return self._name
    
    @model_name.setter
    def model_name(self, name):
        if isinstance(name, str):
            self._name = name
        else:
            raise AttributeError
        
    @property
    def model_root(self):
        return self._parent_dir
    
    @model_root.setter
    def model_root(self, root_dir):
        if not os.path.isdir(root_dir):
            os.makedirs(dir)
        self._parent_dir = root_dir
        
    @property
    def rfactor(self):
        return self._rfactor
    
    def import_project(self, dir):
        pass
    
    def load(self, cfg=None):
        if cfg is None:
            dir = os.path.join(self.model_root, self.model_name)
            base = os.path.join(dir, self.model_name)
            cfg = os.path.join(base) 
        if os.path.isfile(cfg):
            pass

    