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
    def __init__(self, parent=None, color=None):
        super(ColorComboBox, self).__init__(parent)
        
        self.addItems([str(color) for color in QtGui.QColor.colorNames()] + 
                      ['<Custom Color>'])
        
        self.color = color
    
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, color):
        self._color = color


class BrushWidget(QtGui.QWidget):
    """ Widget class for controlling brush options """
    
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
    
    def __init__(self, parent=None, brush=None):
        super(self.__class__, self).__init__(parent)
        
        # set brush
        self.brush = brush or QtGui.QBrush()
        
        layout = QtGui.QGridLayout()
        
        fill_label = QtGui.QLabel("Brush Fill")
        layout.addWidget(fill_label, 1, 0)
        fill_combo = QtGui.QComboBox()
        fill_combo.addItems(self.FILL_STYLES.keys())
        layout.addWidget(fill_combo, 1, 1)
        
        color_label = QtGui.QLabel("Fill Color")
        layout.addWidget(color_label, 2, 0)
        color_combo = ColorComboBox()
        layout.addWidget(color_combo, 2, 1)
        fill_color = ColorButton()
        layout.addWidget(fill_color, 2, 2)

        color_label_2 = QtGui.QLabel("Fill Color 2")
        layout.addWidget(color_label_2, 3, 0)
        color_combo_2 = ColorComboBox()
        layout.addWidget(color_combo_2, 3, 1)
        fill_color_2 = ColorButton()
        layout.addWidget(fill_color_2, 3, 2)
        
        self.setLayout(layout)
        
        
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
    
    def __init__(self, parent=None, pen=None):
        super(self.__class__, self).__init__(parent)
        
        # set pen
        self.pen = pen or QtGui.QPen()
        
        # set layout and associated widgets
        layout = QtGui.QGridLayout()
        
        width_label = QtGui.QLabel("Pen Width")
        layout.addWidget(width_label, 1, 0)
        width_spinbox = QtGui.QDoubleSpinBox()
        layout.addWidget(width_spinbox, 1, 1)
        
        style_label = QtGui.QLabel("Pen Style")
        layout.addWidget(style_label, 2, 0) 
        style_combo = QtGui.QComboBox()
        style_combo.addItems(self.STYLES.keys())
        layout.addWidget(style_combo, 2, 1)
        
        cap_label = QtGui.QLabel("Pen Cap")
        layout.addWidget(cap_label, 3, 0)
        cap_combo = QtGui.QComboBox()
        cap_combo.addItems(self.CAPS.keys())
        layout.addWidget(cap_combo, 3, 1)
        
        join_label = QtGui.QLabel("Pen Join")
        layout.addWidget(join_label, 4, 0)
        join_combo = QtGui.QComboBox()
        join_combo.addItems(self.JOINS.keys())
        layout.addWidget(join_combo, 4, 1)
        
        color_label = QtGui.QLabel("Pen Color")
        layout.addWidget(color_label, 5, 0)
        color_combo = ColorComboBox()
        layout.addWidget(color_combo, 5, 1)
        color_button = ColorButton()
        layout.addWidget(color_button, 5, 2)
        
        self.setLayout(layout)
        
            
class PainterWidget(QtGui.QWidget):
    """ Widget for controlling painter options including pen & brush options """
    def __init__(self, parent=None, pen=None, brush=None):
        super(self.__class__, self).__init__(parent)
        
        layout = QtGui.QVBoxLayout()
        
        more_widget = QtGui.QWidget()
        hlayout = QtGui.QHBoxLayout()
        antialias_checkbox = QtGui.QCheckBox("Antialising")
        hlayout.addWidget(antialias_checkbox)
        more_widget.setLayout(hlayout) 
        
        penWidget = PenWidget(parent, pen)
        brushWidget = BrushWidget(parent, brush)
        
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