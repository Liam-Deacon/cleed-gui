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

import sys
import os

from OpenGL.GL import *
from OpenGL.GLU import *

from qtbackend import QtCore, QtGui
from qtbackend.QtOpenGL import *
from qtbackend.QtCore import Qt

import pymol2
from pymol import _cmd
from copy import deepcopy

class RedirectStdStreams(object):
    def __init__(self, stdout=None, stderr=None):
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush(); self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush(); self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr


class PymolQtWidget(QGLWidget):
    _buttonMap = {Qt.LeftButton: 0,
                  Qt.MidButton: 1,
                  Qt.RightButton: 2}
    '''PyQt pymol widget class using GL canvas'''

    def __init__(self, parent, enable_ui, filename="", unit_cell=False):
        f = QGLFormat()
        f.setStencil(True)
        f.setRgba(True)
        f.setDepth(True)
        f.setDoubleBuffer(True)
        QGLWidget.__init__(self, f, parent=parent)
        self.setMinimumSize(250, 250)
        self._enable_ui = enable_ui
        
        
        # set pymol invocation options
        self.pymol = pymol2.PyMOL()  # _pymolPool.getInstance()
        self.pymol.invocation.options.quiet = 1     
        del(self.pymol._COb, self.pymol.cmd)   
        self.pymol._COb = _cmd._new(self.pymol,self.pymol.invocation.options)
        self.pymol.cmd = pymol2.cmd2.Cmd(self.pymol, self.pymol._COb)
        
        self.pymol.start()
        
        # other initialisation
        self.cmd = self.pymol.cmd
        self.model_name = os.path.basename(os.path.splitext(filename)[0])
        self.zoom_level = 1
        # self.toPymolName = self.pymol.toPymolName ### Attribute Error
        self._pymolProcess()
        
        if not self._enable_ui:
            self.pymol.cmd.set("internal_gui", 0)
            self.pymol.cmd.set("internal_feedback", 0)
            self.pymol.cmd.button("double_left", "None", "None")
            self.pymol.cmd.button("single_right", "None", "None")

        #self.pymol.start()
        
        self.pymol.cmd.bg_color(color="white")
        self.load(filename)
        self.pymol.cmd.do("set antialias, 1")
        self.pymol.cmd.do("set ray_trace_mode, 1")
        self.pymol.cmd.do("show_as spheres")
        self.pymol.cmd.do("set sphere_mode, 4")
        self.pymol.cmd.do("set internal_gui=0")
        self.pymol.cmd.do("zoom center, {}".format(self.zoom_level))
        self._show_cell(unit_cell)
        self.pymol.reshape(self.width(), self.height())
        self.pymol.cmd.viewport(self.width(), self.height())
        self._timer = QtCore.QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._pymolProcess)
        self.resizeGL(self.width(), self.height())
        #globalSettings.settingsChanged.connect(self._updateGlobalSettings)
        self._updateGlobalSettings()
        #self.save(r'C:\Users\kss07698\Desktop\test.mol')
    
    def load(self, File=None):
        if os.path.exists(File):
            self.pymol.cmd.load(File)
            
    def __del__(self):
        pass

    def _updateGlobalSettings(self):
        #for k,v in globalSettings.settings.iteritems():
        #    self.pymol.cmd.set(k, v)
        #self.update()
        return

    def redoSizing(self):
        self.resizeGL(self.width(), self.height())

    def paintGL(self):
        glViewport(0, 0, self.width(), self.height())
        bottom = self.mapToGlobal(QtCore.QPoint(0, self.height())).y()
        #self.pymol.cmd.set("_stencil_parity", bottom & 0x1)
        self._doIdle()
        self.pymol.draw()

    def mouseMoveEvent(self, ev):
        self.pymol.drag(ev.x(), self.height() - ev.y(), 0)
        self._pymolProcess()

    def mousePressEvent(self, event):
        # reimplement right mouse button
        if event.button() == Qt.RightButton:
            print('right-click!')
        else:
            if not self._enable_ui:
                self.pymol.cmd.button("double_left", "None", "None")
                self.pymol.cmd.button("single_right", "None", "None")
            self.pymol.button(self._buttonMap[event.button()], 0, 
                              event.x(), self.height() - event.y(), 0)
            #self._pymolProcess()

    def mouseReleaseEvent(self, event):
        self.pymol.button(self._buttonMap[event.button()], 1, 
                          event.x(), self.height() - event.y(), 0)
        self._pymolProcess()
        self._timer.start(0)

        self.cmd.do("iterate_state 1, sele, print name, x, y, z")

    def wheelEvent(self, event):
        zoom_delta =  1 if (-1 * event.delta()) > 0 else -1
        if self.zoom_level >= 10: 
            zoom_delta *= int(self.zoom_level/10) * 2
        elif self.zoom_level == 1 and zoom_delta < 0:
            zoom_delta = 0
        
        if abs(zoom_delta) > 0: 
            self.zoom_level += zoom_delta
            self.zoom_level = abs(self.zoom_level)
            self.pymol.cmd.do("zoom center, {}".format(self.zoom_level))
            self.update()
        
    def resizeGL(self, w, h):
        self.pymol.reshape(w, h, True)
        self._pymolProcess()

    def initializeGL(self):
        pass
    

    def _pymolProcess(self):
        self._doIdle()
        self.update()

    def _doIdle(self):
        if self.pymol.idle():
            self._timer.start(0)

    def save(self, filename, *args):
        '''save an image of the model'''
        self.pymol.cmd.save(filename, *args)
        
    def _show_cell(self, show):
        if show:
            self.pymol.cmd.do("show cell, {}".format(self.model_name))
        else:
            self.pymol.cmd.do("hide cell, {}".format(self.model_name))

# You don't need anything below this
class PyMolWidgetDemo(QtGui.QMainWindow):
    '''demo class for showing PyMolWidget class''' 
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        usr = os.path.expanduser('~/')
        widget = PymolQtWidget(self, False, 
                               os.path.join(usr, 
                                        r"Dropbox\Structures\spinel111.xyz"),
                               unit_cell=True
                               )
        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QtGui.QApplication(['PyMol Widget Demo'])
    window = PyMolWidgetDemo()
    window.show()
    app.exec_()
