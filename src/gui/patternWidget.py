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
from __future__ import division, with_statement, unicode_literals

from qtbackend import QtCore, QtGui
from qtbackend.QtGui import QGraphicsItem
import res_rc
from operator import isCallable

import sys
import os

try:
    from core import pattern
except ImportError:
    module_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    module_path = os.path.join(module_path, 'core')
    sys.path.insert(0, module_path)
    import pattern

class CirclePath(QtGui.QGraphicsPathItem):
    def __init__(self, parent=None, pos=(0, 0), pen=None, brush=None):
        super(CircleItem, self).__init__(parent)
        
        self._pos = pos
        self._pen = pen
        self._brush = brush

class TriangleItem(QtGui.QGraphicsPolygonItem):
    def __init__(self, parent=None):
        super(TriangleItem, self).__init__(parent)

class SquareItem(QtGui.QGraphicsPolygonItem):
    def __init__(self, parent=None):
        super(SquareItem, self).__init__(parent)

class RhombusItem(QtGui.QGraphicsPolygonItem):
    def __init__(self, parent=None):
        super(RhombusItem, self).__init__(parent)

class StarItem(QtGui.QGraphicsPolygonItem):
    def __init__(self, parent=None):
        super(StarItem, self).__init__(parent)

class HexagonItem(QtGui.QGraphicsPolygonItem):
    def __init__(self, parent=None):
        super(HexagonItem, self).__init__(parent)

class PatternScene(QtGui.QGraphicsScene):
    def _init__(self, parent=None):
        super(PatternScene, self).__init__(parent)

class PatternWidget(QtGui.QGraphicsView):
    """
    Widget for LEED pattern
    """
    lastDir = os.path.expanduser('~')
    lastFile = ''
    filters = ["Pattern Files (*.patt)", "All Files (*)"]
    export_filters = ["SVG (*.svg)", "Postscript (*.ps)", "PDF (*.pdf)", 
                      "TIFF Image (*.tiff)", "PNG Image (*.png)",
                      "BMP Files (*.bmp)", "JPEG Image (*.JPEG)"]
    colorSequence = ['black', 'red', 'blue', 'green', 'orange', 'pink', 'cyan',
                     'yellow', 'gray', 'brown']
    shapeSequence = ['circle', 'triangle_up', 'triangle_down', 'square', 
                     'rhombus', 'star', 'hexagon']
    
    def __init__(self, parent=None):
        super(PatternWidget, self).__init__(parent)
        self.setWindowTitle('Pattern')
        self.setWindowIcon(QtGui.QIcon(':/pattern.svg'))
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setFocus()
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.centerOn(0, 0)
        self.resize(400, 400)
        self.spotSize = 30
        
        brush = QtGui.QBrush(QtGui.QColor(self.colorSequence[0]), 
                             QtCore.Qt.NoBrush)
        pen = QtGui.QPen(brush, 10, QtCore.Qt.SolidLine)
        pen.setColor(QtGui.QColor(brush.color()))
        pen.setCapStyle(QtCore.Qt.FlatCap)
        pen.setWidth(self.spotSize/8)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        self.pen = pen
        
        scene = PatternScene()
        self.setScene(scene)
        
        text = QtGui.QGraphicsTextItem("No Pattern - right click to open", 
                                       scene=scene)
        text.setPos(0, 0)
        
        # handles for grouped items
        self.spots = {'substrate': [], 'superstructures': [[]]}
        self.indices = {'substrate': [], 'superstructures': [[]]}
        self.vectors = {'substrate': [], 'superstructures': [[]]}
        
        self.pattern = pattern.Pattern()
        
        # setup actions & menus
        self.contextMenu = QtGui.QMenu()
        
        self.openAction = QtGui.QAction(QtGui.QIcon(':/folder_fill.svg'),
                                   "&Open", self,
                                   triggered=self.open,
                                   shortcut="Ctrl+O")
        self.openAction.setToolTip("Open pattern file...")
        self.contextMenu.addAction(self.openAction)
        self.addAction(self.openAction)
        
        self.saveAction = QtGui.QAction(QtGui.QIcon(':/save.svg'),
                                   "&Save", self,
                                   triggered=self.save,
                                   shortcut="Ctrl+S")
        self.saveAction.setToolTip("Save pattern...")
        self.contextMenu.addAction(self.saveAction)
        self.addAction(self.saveAction)
        
        # setup connections
        self.customContextMenuRequested.connect(self.rightClickContextMenu)
        
    def rightClickContextMenu(self, point):
        self.contextMenu.popup(self.viewport().mapToGlobal(point))
    
    def open(self, filename=None):
        """ Opens a pattern file """
        if not filename:
            fd = QtGui.QFileDialog()
            fd.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            filename = str(fd.getOpenFileName(self, 
                                              caption="Open Pattern file...",
                                              directory=self.lastDir,
                                              filter=';;'.join(self.filters)))
        if os.path.isfile(filename):
            self.lastDir = os.path.dirname(filename)
            self.lastFile = filename
            try:
                self.pattern = pattern.Pattern.read(filename)
            except:
                return
            
            self.draw()
        
            
    def save(self, filename=None):
        """ Saves the pattern """
        if not filename:
            fd = QtGui.QFileDialog()
            fd.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            filters = self.filters[:1] + self.export_filters
            filename = str(fd.getSaveFileName(self, 
                                              caption='Save Pattern...', 
                                              directory=self.lastDir,
                                              filter=';;'.join(filters)))
        
        if not filename:
            return
            
        self.lastDir = os.path.dirname(filename)
        self.lastFile = filename 
        
        # use QPrinter for vector formats
        if os.path.splitext(filename)[1].lower() in ('pdf', 'ps', 'svg'):
            printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
            printer.setPageSize(QtGui.QPrinter.A4)
            printer.setOrientation(QPrinter.Portrait)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName("test.pdf") 
 
            p = QtGui.QPainter(self)
 
            if not p.begin(printer):
                QtGui.QMessageBox(self) # error
                return
    
            self.scene.render(p)
            p.end()
        else:
            pixmap = QtGui.QPixmap()
            painter = QtGui.QPainter(pixmap)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            scene.render(painter)
            painter.end()
            pixMap.save(fileName)
            
    
    def draw(self):
        spots = {'substrate': self.pattern.calculate_spots(), 
                 'superstructures': [dom.calculate_spots() 
                                    for dom in self.pattern.domains]}
        
        try:
            self.scene().removeItem(self.spots['substrate'])
        except:
            pass
        for group in ['spots', 'indices', 'vectors']:
            for domainGroup in eval("self.{}['superstructures']".format(group)):
                try:
                    self.scene().removeItem(domainGroup)
                    # maybe forcibly delete domainGroup here
                    # rather than relying on Python's garbage collection
                except:
                    continue
        
        # create new groups
        for group in ['spots', 'indices', 'vectors']:
            obj = eval('self.{}'.format(group))
            obj['substrate'] = QtGui.QGraphicsItemGroup(self, self.scene())
            obj['superstructures'] = [QtGui.QGraphicsItemGroup(self, self.scene())
                                      for item in spots['superstructures']]
        

        for spot in spots['substrate']:
            self.indices['substrate'].addToGroup(self.draw_label(spot))
            
    
    def draw_label(self, spot, pen=None, brush=None, font=None, **kwargs):
        label = QtGui.QGraphicsTextItem('{},{}'.format(*spot.index()))
        label.setPos(*spot.pos())
        label.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        label.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        if hasattr(pen, 'color') and callable(pen.color):
            label.setDefaultTextColor(pen.color())
        
        if not isinstance(font, QtGui.QFont):
            size = kwargs['size'] if 'size' in kwargs else self.spotSize
            font = QtGui.QFont("Times", size, 800)
        label.setFont(font)
        
        return label
        
    def draw_spot(self, spot, path, pen=None, brush=None, font=None, **kwargs):
        pass
    
    def wheelEvent(self, event):
        delta = event.delta() 
        if (self.zoom <= 0.1 and delta < 0) or (self.zoom >= 10 and delta > 0):
            return
            
        # perform zoom 
        scaling = 1.1 if delta > 0 else 0.9
        self.scale(scaling, scaling)
        self.zoom *= scaling 

if __name__ == '__main__':
    import sys
    
    app = QtGui.QApplication(sys.argv)
    
    pat = PatternWidget()
    pat.show()
    pat.resize(800, 600)
    
    
    app.exec_()
    