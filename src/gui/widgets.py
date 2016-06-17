##############################################################################
# Author: Liam Deacon                                                        #
#                                                                            #
# Contact: liam.m.deacon@gmail.com                                           #
#                                                                            #
# Copyright: Copyright (C) 2016 Liam Deacon                                  #
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
**widgets.py** - module containing various custom widgets for common functionality.
'''
from __future__ import (print_function, unicode_literals, absolute_import, 
                        division, with_statement)

from qtbackend import QtGui, QtCore
from collections import OrderedDict

try:
    from matplotlib.backends.qt_editor.formlayout import ColorButton
except ImportError:
    import sys
    sys.stderr.write("Could not load ColorButton from matplotlib")
    class ColorButton(QtGui.QPushButton):
        """ Create crude approximation of ColorButton """
        def __init__(self, parent=None, color=None):
            super(ColorButton, self).__init__(parent)            
        
class ColorComboBox(QtGui.QComboBox):
    """ A combo box for selecting a color """
    
    COLOR_NAMES = list(QtGui.QColor.colorNames())
    PIXMAP_SIZE = (16, 16)
    
    colorChanged = QtCore.Signal(QtGui.QColor)
    customColorUpdated = QtCore.Signal(bool)
    
    def __init__(self, parent=None, color=None):
        super(ColorComboBox, self).__init__(parent)
        
        self.custom_color = QtGui.QColor("black") 
        
        for color in self.COLOR_NAMES + ['<Custom Color>']:
            color = str(color)
            try:
                pixmap = QtGui.QPixmap(*self.PIXMAP_SIZE)
                pixmap.fill(QtGui.QColor(color))
                self.addItem(QtGui.QIcon(pixmap), color)
            except:
                self.addItem(color)
        
        self.currentIndexChanged.connect(self.updateColor)
        self.activated.connect(self.updateColor)
        
        # set up custom color
        self.dlg = QtGui.QColorDialog()
        self.dlg.setCurrentColor(self.custom_color)
        self.custom_colors = []
        self.dlg.setCustomColor(0, self.custom_color.rgba())
        
        self.dlg.currentColorChanged.connect(self.updateCustomColor)
        self.dlg.finished.connect(self.customColorUpdated.emit)
        
        self.customColorUpdated.connect(self.updateColor)
        self.color = color
    
    
    def updateColor(self, color_value):
        # check whether boolean from dialog
        if color_value is True:
            pixmap = QtGui.QPixmap(*self.PIXMAP_SIZE)
            pixmap.fill(QtGui.QColor(self.custom_color))
            self.setItemIcon(len(self.COLOR_NAMES), QtGui.QIcon(pixmap))
            self.color = self.custom_color 
            self.colorChanged.emit(self.color)
            self.updateCustomColors()
            return
        
        # assume index of combo box
        if color_value == len(self.COLOR_NAMES):
            self.dlg.show()
        else:
            color = self.itemText(color_value)
            self.color = QtGui.QColor(color)
            self.colorChanged.emit(self.color)
    
    def updateCustomColor(self, color):
        self.custom_color = color
        
    def updateCustomColors(self):
        n_max = self.dlg.customCount()
        n = len(self.custom_colors)
        if n >= n_max:
            self.custom_colors.pop(-1)
        if n == 0 or self.custom_color.rgba() != self.custom_colors[0].rgba():
            self.custom_colors.insert(0, self.custom_color)
            for i in range(len(self.custom_colors)):
                self.dlg.setCustomColor(i, self.custom_colors[i].rgba())
    
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, color):
        self._color = color
        

class BrushWidget(QtGui.QWidget):
    """ Widget class for controlling brush options 
    
    Attributes
    ----------
    
    FILL_STYLES: dictionary of different supported fill styles
    
    brushChanged: signal emitted when brush is altered.
    
    """
    
    FILL_STYLES = OrderedDict((
                    ('Solid', QtCore.Qt.SolidPattern),
                    ('Linear Gradient', QtCore.Qt.LinearGradientPattern),
                    ('Conical Gradient', QtCore.Qt.ConicalGradientPattern),
                    ('Radial Gradient', QtCore.Qt.RadialGradientPattern),
                    ('Texture', QtCore.Qt.TexturePattern),
                    ('Horizontal', QtCore.Qt.HorPattern),
                    ('Vertical', QtCore.Qt.VerPattern),
                    ('Cross', QtCore.Qt.CrossPattern),
                    ('Backward Diagonal', QtCore.Qt.BDiagPattern),
                    ('Forward Diagonal', QtCore.Qt.FDiagPattern),
                    ('Diagonal Cross', QtCore.Qt.DiagCrossPattern),
                    ('Dense 1', QtCore.Qt.Dense1Pattern),
                    ('Dense 2', QtCore.Qt.Dense2Pattern),
                    ('Dense 3', QtCore.Qt.Dense3Pattern),
                    ('Dense 4', QtCore.Qt.Dense4Pattern),
                    ('Dense 5', QtCore.Qt.Dense5Pattern),
                    ('Dense 6', QtCore.Qt.Dense6Pattern),
                    ('Dense 7', QtCore.Qt.Dense7Pattern),
                    ('None', QtCore.Qt.NoBrush),
                    )
                )
    
    brushChanged = QtCore.Signal(QtGui.QBrush)
    
    def __init__(self, parent=None, brush=None):
        """
        Initialises BrushWidget instance.
        
        Arguments
        ---------
        parent: widget to belong to (or None)
        brush: brush to use, otherwise use default.
        """
        super(self.__class__, self).__init__(parent)
        
        # set brush
        self.brush = brush or QtGui.QBrush()
        
        layout = QtGui.QGridLayout()
        
        fill_label = QtGui.QLabel("Fill Style")
        layout.addWidget(fill_label, 1, 0)
        fill_combo = QtGui.QComboBox()
        fill_combo.setToolTip("Choose shape fill style")
        fill_combo.addItems(self.FILL_STYLES.keys())
        layout.addWidget(fill_combo, 1, 1)
        
        color_label = QtGui.QLabel("Fill Color")
        layout.addWidget(color_label, 2, 0)
        color_combo = ColorComboBox()
        color_combo.setToolTip("Choose primary fill color")
        layout.addWidget(color_combo, 2, 1)
        fill_color_1 = ColorButton()
        fill_color_1.setToolTip("Choose custom color for primary brush fill")
        layout.addWidget(fill_color_1, 2, 2)

        color_label_2 = QtGui.QLabel("Fill Color 2")
        layout.addWidget(color_label_2, 3, 0)
        color_combo_2 = ColorComboBox()
        color_combo_2.setToolTip("Choose secondary fill color")
        layout.addWidget(color_combo_2, 3, 1)
        fill_color_2 = ColorButton()
        fill_color_2.setToolTip("Choose custom color for secondary brush fill")
        layout.addWidget(fill_color_2, 3, 2)

        color_label_3 = QtGui.QLabel("Fill Color 3")
        layout.addWidget(color_label_3, 4, 0)
        color_combo_3 = ColorComboBox()
        color_combo_3.setToolTip("Choose tertiary fill color")
        layout.addWidget(color_combo_3, 4, 1)
        fill_color_3 = ColorButton()
        fill_color_3.setToolTip("Choose custom color for tertiary brush fill")
        layout.addWidget(fill_color_3, 4, 2)
        
        self.setLayout(layout)
        
    def _populateFillStyles(self):
        raise NotImplementedError("TODO")
    
        size = 160
        for i, cap in enumerate(self.CAPS):
            pixmap = QtGui.QPixmap(size, size) 
            pixmap.fill(QtCore.Qt.transparent)   
            painter = QtGui.QPainter(pixmap)
            pen = QtGui.QPen(self.pen)
            pen.setWidth(0.25*size)
            pen.setCapStyle(self.CAPS[cap])
            painter.setPen(pen)
            painter.drawLine(0.25*size, 0.25*size, 0.25*size, 0.75*size)
            painter.drawLine(0.25*size, 0.75*size, 0.75*size, 0.75*size)
            self.cap_combo.setItemIcon(i, QtGui.QIcon(pixmap))
            del(painter)
        
        
class PenWidget(QtGui.QWidget):
    """ Widget Class for controlling pen options """
    
    CAPS = {'Flat': QtCore.Qt.FlatCap, 
            'Square': QtCore.Qt.SquareCap, 
            'Round': QtCore.Qt.RoundCap}
    COLORS = {}
    JOINS = {'Miter': QtCore.Qt.MiterJoin,
             'Bevel': QtCore.Qt.BevelJoin,
             'Round': QtCore.Qt.RoundJoin}
    STYLES = {'Solid': QtCore.Qt.SolidLine,
              'Dash': QtCore.Qt.DashLine,
              'Dot': QtCore.Qt.DotLine,
              'Dash Dot': QtCore.Qt.DashDotLine,
              'Dash Dot Dot': QtCore.Qt.DashDotDotLine,
              'None' : QtCore.Qt.NoPen,
              }
    PIXMAP_SIZE = 160
    
    penChanged = QtCore.Signal(QtGui.QPen)
    
    def __init__(self, parent=None, pen=None):
        super(self.__class__, self).__init__(parent)
        
        # set pen
        self.pen = pen or QtGui.QPen()
        
        # set layout and associated widgets
        layout = QtGui.QGridLayout()
        
        width_label = QtGui.QLabel("Pen Width")
        layout.addWidget(width_label, 1, 0)
        width_spinbox = QtGui.QDoubleSpinBox()
        width_spinbox.setToolTip("Sets the line thickness")
        layout.addWidget(width_spinbox, 1, 1)
        width_spinbox.valueChanged.connect(self.setPenWidth)
        
        style_label = QtGui.QLabel("Dash Style")
        layout.addWidget(style_label, 2, 0) 
        style_combo = QtGui.QComboBox()
        style_combo.setToolTip("Chooses a line style")
        style_combo.addItems(self.STYLES.keys())
        layout.addWidget(style_combo, 2, 1)
        self.dash_combo = style_combo
        self._populatePenStyleIcons()
        self.dash_combo.activated.connect(self.setPenStyle)
        self.dash_combo.currentIndexChanged.connect(self.setPenStyle)
        
        cap_label = QtGui.QLabel("Cap Style")
        layout.addWidget(cap_label, 3, 0)
        cap_combo = QtGui.QComboBox()
        cap_combo.setToolTip("Chooses a line capping")
        cap_combo.addItems(self.CAPS.keys())
        layout.addWidget(cap_combo, 3, 1)
        self.cap_combo = cap_combo
        self._populateCapStyleIcons()
        self.cap_combo.activated.connect(self.setCapStyle)
        self.cap_combo.currentIndexChanged.connect(self.setCapStyle)
        
        join_label = QtGui.QLabel("Join Style")
        layout.addWidget(join_label, 4, 0)
        join_combo = QtGui.QComboBox()
        join_combo.setToolTip("Chooses a line joining")
        join_combo.addItems(self.JOINS.keys())
        layout.addWidget(join_combo, 4, 1)
        self.join_combo = join_combo
        self._populateJoinStyleIcons()
        self.join_combo.activated.connect(self.setJoinStyle)
        self.join_combo.currentIndexChanged.connect(self.setJoinStyle)
        
        color_label = QtGui.QLabel("Pen Color")
        layout.addWidget(color_label, 5, 0)
        color_combo = ColorComboBox()
        color_combo.setToolTip("Choose a color for the line")
        layout.addWidget(color_combo, 5, 1)
        self.color_combo = color_combo
        self.color_combo.activated.connect(self.setColor)
        self.color_combo.currentIndexChanged.connect(self.setColor)
        
        color_button = ColorButton()
        color_button.setToolTip("Choose a custom color for the line")
        layout.addWidget(color_button, 5, 2)
        self.color_button = color_button
        
        self.setLayout(layout)
        
        self.penChanged.connect(lambda x: print(x))
        
    def _populateCapStyleIcons(self):
        """ Populates cap_combo items with icons for the different cap styles"""
        size = self.PIXMAP_SIZE
        for i, cap in enumerate(self.CAPS):
            pixmap = QtGui.QPixmap(size, size) 
            pixmap.fill(QtCore.Qt.transparent)   
            painter = QtGui.QPainter(pixmap)
            pen = QtGui.QPen(self.pen)
            pen.setWidth(0.25*size)
            pen.setCapStyle(self.CAPS[cap])
            painter.setPen(pen)
            painter.drawLine(0.25*size, 0.25*size, 0.25*size, 0.75*size)
            painter.drawLine(0.25*size, 0.75*size, 0.75*size, 0.75*size)
            self.cap_combo.setItemIcon(i, QtGui.QIcon(pixmap))
            del(painter)

    def _populateJoinStyleIcons(self):
        """ Populates join_combo items with icons for the different join types """
        size = self.PIXMAP_SIZE
        for i, join in enumerate(self.JOINS):
            pixmap = QtGui.QPixmap(size, size) 
            pixmap.fill(QtCore.Qt.transparent)   
            painter = QtGui.QPainter(pixmap)
            pen = QtGui.QPen(self.pen)
            pen.setWidth(size/2.)
            pen.setJoinStyle(self.JOINS[join])
            painter.setPen(pen)
            painter.drawRect((7/16.)*size, (7/16.)*size, size, size)
            self.join_combo.setItemIcon(i, QtGui.QIcon(pixmap))
            del(painter)
     
    def _populatePenStyleIcons(self):
        """ Populates dash_combo items with icons for the different dash types """
        size = self.PIXMAP_SIZE
        for i, style in enumerate(self.STYLES):
            pixmap = QtGui.QPixmap(size, size) 
            pixmap.fill(QtCore.Qt.transparent)   
            painter = QtGui.QPainter(pixmap)
            pen = QtGui.QPen(self.pen)
            pen.setWidth(size/10.)
            pen.setStyle(self.STYLES[style])
            painter.setPen(pen)
            painter.drawLine(0, size/2., size, size/2.)
            self.dash_combo.setItemIcon(i, QtGui.QIcon(pixmap))
            del(painter)
    
    def setCapStyle(self, cap):
        self.pen.setCapStyle(cap)
        self.penChanged.emit(self.pen)
    
    def setColor(self, color):
        if isinstance(color, int):
            self.pen.setColor(self.color_combo.color)
        else:
            raise ValueError(color)
        self.penChanged.emit(self.pen)
    
    def setJoinStyle(self, join):
        self.pen.setJoinStyle(join)
        self.penChanged.emit(self.pen)
    
    def setPenStyle(self, style):
        self.pen.setStyle(style)
        self.penChanged.emit(self.pen)        
    
    def setPenWidth(self, width):
        self.pen.setWidth(width)
        self.penChanged.emit(self.pen)
    
class PainterWidget(QtGui.QWidget):
    """ Widget for controlling painter options including pen & brush options """
    def __init__(self, parent=None, pen=None, brush=None):
        super(self.__class__, self).__init__(parent)
        
        layout = QtGui.QVBoxLayout()
        
        more_widget = QtGui.QWidget()
        hlayout = QtGui.QHBoxLayout()
        antialias_checkbox = QtGui.QCheckBox("Antialising")
        antialias_checkbox.setObjectName("antialias_checkbox")
        antialias_checkbox.setStatusTip("Enables Antialiasing")
        antialias_checkbox.setToolTip("Enables Antialiasing")
        hlayout.addWidget(antialias_checkbox)
        more_widget.setLayout(hlayout) 
        
        penWidget = PenWidget(parent, pen)
        penWidget.setObjectName("penWidget")
        brushWidget = BrushWidget(parent, brush)
        brushWidget.setObjectName("brushWidget")
        
        layout.addWidget(penWidget)
        layout.addWidget(brushWidget)
        layout.addWidget(more_widget)
        
        self.setLayout(layout)
        
        
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    
    window = PainterWidget()
    window.show()
    
    sys.exit(app.exec_())