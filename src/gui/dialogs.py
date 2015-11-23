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
**dialogs.py** - module containing various custom dialogs.
'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

from qtbackend import QtGui, QtCore

import matplotlib as mpl 

import res_rc

class SettingsDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)

class CanvasWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(CanvasWidget, self).__init__(parent)

class AxisScaleWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(AxisScaleWidget, self).__init__(parent)        
        
        axis_from_spinbox = QtGui.QDoubleSpinBox()
        axis_from_spinbox.setToolTip('Specifies the axis maximum')
        axis_from_spinbox.setSingleStep(0.1)
        
        axis_to_spinbox = QtGui.QDoubleSpinBox()
        axis_to_spinbox.setToolTip('Specifies the axis maximum')
        axis_to_spinbox.setSingleStep(0.1)
        
        type_combobox = QtGui.QComboBox()
        
        inverted_checkbox = QtGui.QCheckBox('Inverted')
        
        step_radio = QtGui.QRadioButton('Step')
        major_ticks_radio = QtGui.QRadioButton('Step')
        
        minor_ticks_label = QtGui.QLabel('Minor Ticks')
        minor_ticks_combo = QtGui.QComboBox()
        minor_ticks_combo.setEditable(True)
        for val in (0, 1, 4, 9, 14, 19):
            minor_ticks_combo.addItem(str(val))
            
        axis_break_checkbox = QtGui.QCheckBox('Show Axis Break')
        axis_break_decoration_checkbox = QtGui.QCheckBox('Draw Break Decoration')
        axis_break_from_spinbox = QtGui.QDoubleSpinBox()
        axis_break_to_spinbox = QtGui.QDoubleSpinBox()
        

class GridWidget(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(GridWidget, self).__init__()
    
        color_label = QtGui.QLabel('Line Color')
        type_label = QtGui.QLabel('Line Type')
        thickness_label = QtGui.QLabel('Thickness')
        axes_label = QtGui.QLabel('Axes')
        lines_label = QtGui.QLabel('Lines')
        major_grids_check = QtGui.QCheckBox('Major Grids')
        minor_grids_check = QtGui.QCheckBox('Minor Grids')
        
        major_color = QtGui.QPushButton('')
        minor_color = QtGui.QPushButton('')
        
        minor_linetype_combo = self.new_linetype_combo()
        major_linetype_combo = self.new_linetype_combo()
        
    def new_thickness_spin_box(self):
        box = None
        
    def new_linetype_combo(self):
        combo = QtGui.QComboBox(self)
        
        return combo
        
       
        

class MplBaseDialog(QtGui.QDialog):
    
    families = ['serif', 'sans-serif', 'cursive', 'fantasy', 'monospace']
    linestyles = ['-', '--', '-.', ':', 'None', ' ', '']
    markers = mpl.markers.MarkerStyle.markers
    fill_styles = mpl.markers.MarkerStyle.fillstyles
    caps = mpl.lines.Line2D.validCap
    joins = mpl.lines.Line2D.validJoin
    
    def __init__(self, parent=None):
        super(MplBaseDialog, self).__init__(parent)
    
        layout = QtGui.QVBoxLayout(self)
        
        #self.tab_widget = QtGui.QTabWidget()
        #self.tab_widget.addTab(self, 'test')
        #
        self.font_label = QtGui.QLabel('Font Family:')
        self.size_label = QtGui.QLabel('Size:')
        self.text_label = QtGui.QLabel('Label:')
        self.color_label = QtGui.QLabel('Color:')
        self.alpha_label = QtGui.QLabel('Alpha:')
        self.fill_color_label = QtGui.QLabel("Fill color:")
        self.fill_alpha_label = QtGui.QLabel("Fill alpha:")
        
        self.font_combo = QtGui.QComboBox()
        self.color_combo = QtGui.QComboBox()
        self.text_edit = QtGui.QLineEdit()
        self.size_spin_box = QtGui.QSpinBox()
        self.alpha_spin_box = QtGui.QDoubleSpinBox()
        self.fill_alpha_spin_box = QtGui.QDoubleSpinBox()
        
        try:
            from matplotlib.backends.qt4_editor.formlayout import ColorButton
            self.color_button = ColorButton()
            self.fill_color_button = ColorButton()
        except:
            self.color_button = QtGui.QPushButton('')
            self.color_button.setVisible(False)
            self.fill_color_button = QtGui.QPushButton('')
            self.fill_color_button.setVisible(False)
        
        
        self.bold_check = QtGui.QPushButton('B')
        self.italics_check = QtGui.QPushButton('I')
        self.underline_check = QtGui.QPushButton('U')
        self.underline_check.setVisible(False)  # not yet implemented
        
        font = QtGui.QFont()
        font.setWeight(600)
        self.bold_check.setFont(font)
        self.bold_check.setCheckable(True)
        self.bold_check.setMinimumWidth(25)
        self.bold_check.setSizePolicy(QtGui.QSizePolicy.Minimum, 
                                      QtGui.QSizePolicy.Preferred)
        
        font = QtGui.QFont()
        font.setItalic(True)
        self.italics_check.setFont(font)
        self.italics_check.setCheckable(True)
        self.italics_check.setMinimumWidth(25)
        self.italics_check.setSizePolicy(QtGui.QSizePolicy.Minimum, 
                                         QtGui.QSizePolicy.Preferred)
        
        
        font = QtGui.QFont()
        font.setUnderline(True)
        self.underline_check.setFont(font)
        self.underline_check.setCheckable(True)
        self.underline_check.setMinimumWidth(25)
        self.underline_check.setSizePolicy(QtGui.QSizePolicy.Minimum, 
                                           QtGui.QSizePolicy.Preferred)
        
        self.alpha_spin_box.setMinimum(0.)
        self.alpha_spin_box.setMaximum(1.)
        self.alpha_spin_box.setSingleStep(0.1)
        
        self.fill_alpha_spin_box.setMinimum(0.)
        self.fill_alpha_spin_box.setMaximum(1.)
        self.fill_alpha_spin_box.setSingleStep(0.1)
        
        self.size_spin_box.setMinimum(1)
        self.size_spin_box.setMaximum(200)
        self.size_spin_box.setSingleStep(1)

        self._populate_colors()
        for family in self.families:
            self.font_combo.addItem(family)
        
        spacer = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, 
                                   QtGui.QSizePolicy.Minimum)
        layout.addWidget(self.font_label)
        font_layout = QtGui.QHBoxLayout()
        font_layout.addWidget(self.font_combo)
        font_layout.addWidget(self.bold_check)
        font_layout.addWidget(self.italics_check)
        font_layout.addWidget(self.underline_check)
        font_layout.addItem(spacer)
        layout.addLayout(font_layout)
        
        layout.addWidget(self.size_label)
        layout.addWidget(self.size_spin_box)
        
        layout.addWidget(self.color_label)
        color_layout = QtGui.QHBoxLayout()
        color_layout.addWidget(self.color_combo)
        color_layout.addWidget(self.color_button)
        layout.addLayout(color_layout)
        
        layout.addWidget(self.alpha_label)
        layout.addWidget(self.alpha_spin_box)
        
        #layout.addWidget(self.fill_alpha_label)
        #layout.addWidget(self.fill_alpha_spin_box)
        
        layout.addWidget(self.text_label)
        layout.addWidget(self.text_edit)    
        
    def _populate_colors(self):
        import matplotlib as mpl
        self.colors = dict()
        i = 0
        for name, hex_code in mpl.colors.cnames.iteritems():
            rgb = [channel * 255  for channel in mpl.colors.hex2color(hex_code)]
            pixmap = QtGui.QPixmap(100,100)
            pixmap.fill(QtGui.QColor(*rgb))
            self.color_combo.addItem(name)
            self.color_combo.setItemIcon(i, QtGui.QIcon(pixmap))
            self.colors[name] = i
            i += 1
    
    def _set_text(self, text):
        if len(str(text).lstrip().rstrip()) > 0:
            self.text.set_text(text)
            self.text.set_alpha(1.)
        else:
            self.text.set_text('____')
            self.text.set_alpha(0.)
    
    def callback(self, func):
        ''' Executes `func` then tries to update the matplotlib canvas '''
        func
        try:
            self.parent().canvas.draw()
        except AttributeError:
            pass
    

class MplLegendDialog(MplBaseDialog):
    ''' Live dialog for editing the legend '''
    def __init__(self, parent=None, legend=None):
        super(MplLegendDialog, self).__init__(parent)

        self.setWindowTitle('Edit Legend')
        self.setWindowIcon(QtGui.QIcon(':/list.png'))
        
                

class MplFigureDialog(QtGui.QDialog):
    ''' Live dialog for editing plots '''
    def __init__(self, parent=None, figure=None):
        super(MplFigureDialog, self).__init__(parent)
        
        self.setWindowTitle('Edit plot')
        self.setWindowIcon(QtGui.QIcon(':/graph_dash.png'))
        
        self.bkgnd_color_label = QtGui.QLabel("Background color:")
        self.bkgnd_color_button = ColorButton()
        
    
class MplLabelDialog(QtGui.QDialog):
    ''' Live dialog for editing text labels '''
    
    def __init__(self, parent=None, text=None):
        super(MplLabelDialog, self).__init__(parent)
        
        self.setWindowTitle('Edit text')
        self.setWindowIcon(QtGui.QIcon(':/font_32x32.png'))
        
        layout = QtGui.QVBoxLayout(self)
        
        #self.tab_widget = QtGui.QTabWidget()
        #self.tab_widget.addTab(self, 'test')
        #
        self.font_label = QtGui.QLabel('Font Family:')
        self.size_label = QtGui.QLabel('Size:')
        self.text_label = QtGui.QLabel('Label:')
        self.color_label = QtGui.QLabel('Color:')
        self.alpha_label = QtGui.QLabel('Alpha:')
        self.fill_color_label = QtGui.QLabel("Background color:")
        self.fill_alpha_label = QtGui.QLabel("Background alpha:")
        
        self.font_combo = QtGui.QComboBox()
        self.color_combo = QtGui.QComboBox()
        self.text_edit = QtGui.QLineEdit()
        self.size_spin_box = QtGui.QSpinBox()
        self.alpha_spin_box = QtGui.QDoubleSpinBox()
        self.fill_alpha_spin_box = QtGui.QDoubleSpinBox()
        
        try:
            from matplotlib.backends.qt4_editor.formlayout import ColorButton
            self.color_button = ColorButton()
            self.color_button.colorChanged.connect(lambda x:
                self.callback(self.text.set_color(self.color_button.color)))
        except:
            pass
        
        self.bold_check = QtGui.QPushButton('B')
        self.italics_check = QtGui.QPushButton('I')
        self.underline_check = QtGui.QPushButton('U')
        self.underline_check.setVisible(False)  # not yet implemented
        
        font = QtGui.QFont()
        font.setWeight(600)
        self.bold_check.setFont(font)
        self.bold_check.setCheckable(True)
        self.bold_check.setMinimumWidth(25)
        self.bold_check.setSizePolicy(QtGui.QSizePolicy.Minimum, 
                                      QtGui.QSizePolicy.Preferred)
        
        font = QtGui.QFont()
        font.setItalic(True)
        self.italics_check.setFont(font)
        self.italics_check.setCheckable(True)
        self.italics_check.setMinimumWidth(25)
        self.italics_check.setSizePolicy(QtGui.QSizePolicy.Minimum, 
                                         QtGui.QSizePolicy.Preferred)
        
        
        font = QtGui.QFont()
        font.setUnderline(True)
        self.underline_check.setFont(font)
        self.underline_check.setCheckable(True)
        self.underline_check.setMinimumWidth(25)
        self.underline_check.setSizePolicy(QtGui.QSizePolicy.Minimum, 
                                           QtGui.QSizePolicy.Preferred)
        
        self.alpha_spin_box.setMinimum(0.)
        self.alpha_spin_box.setMaximum(1.)
        self.alpha_spin_box.setSingleStep(0.1)
        
        self.fill_alpha_spin_box.setMinimum(0.)
        self.fill_alpha_spin_box.setMaximum(1.)
        self.fill_alpha_spin_box.setSingleStep(0.1)
        
        self.size_spin_box.setMinimum(1)
        self.size_spin_box.setMaximum(200)
        self.size_spin_box.setSingleStep(1)

        self._populate_fonts()
        self._populate_colors()
        
        spacer = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, 
                                   QtGui.QSizePolicy.Minimum)
        layout.addWidget(self.font_label)
        font_layout = QtGui.QHBoxLayout()
        font_layout.addWidget(self.font_combo)
        font_layout.addWidget(self.bold_check)
        font_layout.addWidget(self.italics_check)
        font_layout.addWidget(self.underline_check)
        font_layout.addItem(spacer)
        layout.addLayout(font_layout)
        
        layout.addWidget(self.size_label)
        layout.addWidget(self.size_spin_box)
        
        layout.addWidget(self.color_label)
        color_layout = QtGui.QHBoxLayout()
        color_layout.addWidget(self.color_combo)
        if hasattr(self, 'color_button'):
            color_layout.addWidget(self.color_button)
        layout.addLayout(color_layout)
        
        layout.addWidget(self.alpha_label)
        layout.addWidget(self.alpha_spin_box)
        
        #layout.addWidget(self.fill_alpha_label)
        #layout.addWidget(self.fill_alpha_spin_box)
        
        layout.addWidget(self.text_label)
        layout.addWidget(self.text_edit)    
        
        #self.addLayout(layout)
        
        self.text = text
        
        try:
            import matplotlib as mpl
        
            self.size_spin_box.setValue(text.get_size() or 12)
            self.text_edit.setText(text.get_text() if text.get_text() != '____' else '')
            self.font_combo.setCurrentIndex(self.families.index(text.get_family()[0]))
            self.font_combo.update()
            color = text.get_color()
            try:
                self.font_combo.setCurrentIndex(self.colors[color])
            except KeyError:
                from matplotlib.colors import ColorConverter, rgb2hex, cnames
                code = rgb2hex(ColorConverter.colors[color])
                
                for name in cnames:
                    if cnames[name] == code:
                        color = name
                
                try:        
                    self.font_combo.setCurrentIndex(self.colors[color])
                except KeyError:
                    self.font_combo.setCurrentIndex(self.colors['black'])
            finally:
                pass
            
            try:
                self.bold_check.setChecked((text.get_weight() >= 600))
            except:
                pass
            
            try: 
                self.italics_check.setChecked(text.get_style() == 'italic')
            except:
                pass
            
        except ImportWarning:
            pass
        
        self.text_edit.textChanged.connect(lambda x: self.callback(self._set_text(x)))
        self.color_combo.currentIndexChanged.connect(lambda x: 
            self.callback(self.text.set_color(str(self.color_combo.itemText(x)))))
        self.font_combo.currentIndexChanged.connect(lambda x: 
            self.callback(self.text.set_family(str(self.font_combo.itemText(x)))))
        self.size_spin_box.valueChanged.connect(lambda x: 
                                        self.callback(self.text.set_size(x)))
        self.alpha_spin_box.valueChanged.connect(lambda x:
                                        self.callback(self.text.set_alpha(x)))
        
        self.bold_check.toggled.connect(lambda x:
                self.callback(self.text.set_weight('bold' if x else 'normal')))
        self.italics_check.toggled.connect(lambda x:
                self.callback(self.text.set_style('italic' if x else 'normal')))
        self.underline_check.toggled.connect(lambda x:
                self.callback(self.text.set_text('\\underline{%s}'
                                                 % self.text.get_text() if x 
                                                 else self.text.get_text())))
        

class MplAxisDialog(MplBaseDialog):
    ''' Live dialog for editing axis '''
    def __init__(self, parent=None, axis=None):
        super(MplFigureDialog, self).__init__(parent)
        
        axis = mpl.axis.Axis()
        
        if isinstance(axis, mpl.axis.XAxis):
            ax = 'X-Axis'
        elif isinstance(axis, mpl.axis.YAxis):
            ax = 'Y-Axis'
        else:
            ax = 'Axis'
        self.setWindowTitle('Edit {}'.format(ax))
        self.setWindowIcon(QtGui.QIcon(':/graph_dash.png'))
        
        
        self.text = axis
    
        self.text_edit.textChanged.connect(lambda x: self.callback(self._set_text(x)))
        self.color_combo.currentIndexChanged.connect(lambda x: 
            self.callback(self.text.set_color(str(self.color_combo.itemText(x)))))
        self.font_combo.currentIndexChanged.connect(lambda x: 
            self.callback(self.text.set_family(str(self.font_combo.itemText(x)))))
        self.size_spin_box.valueChanged.connect(lambda x: 
                                        self.callback(self.text.set_size(x)))
        self.alpha_spin_box.valueChanged.connect(lambda x:
                                        self.callback(self.text.set_alpha(x)))
        
        self.bold_check.toggled.connect(lambda x:
                self.callback(self.text.set_weight('bold' if x else 'normal')))
        self.italics_check.toggled.connect(lambda x:
                self.callback(self.text.set_style('italic' if x else 'normal')))
        self.underline_check.toggled.connect(lambda x:
                self.callback(self.text.set_text('\\underline{%s}'
                                                 % self.text.get_text() if x 
                                                 else self.text.get_text())))
        

class SmoothDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(SmoothDialog, self).__init__(parent)

        self.setWindowTitle('Smooth IV')
        self.setWindowIcon(QtGui.QIcon(':/graph_smooth.svg'))

        layout = QtGui.QVBoxLayout(self)

        # combo box for multiple plots
        layout.addWidget(QtGui.QLabel('Data set:'))
        self.combo = QtGui.QComboBox()
        layout.addWidget(self.combo)
        for item in self.parent().legend_labels:
            self.combo.addItem(item)

        # OK and Cancel buttons
        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | 
                                         QtGui.QDialogButtonBox.Cancel,
                                         QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_dataset(self):
        return self.combo.currentIndex()