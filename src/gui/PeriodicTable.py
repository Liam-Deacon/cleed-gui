#!/usr/bin/env python
#encoding: utf-8
#
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

"""
atorb.py

@author: Liam Deacon

@contact: liam.m.deacon@gmail.com

@copyright: Copyright (C) 2014-2015 Liam Deacon

@license: MIT License (see LICENSE file for details)

@summary: Periodic Table using Qt

"""

# Import standard libraries
import logging
import ntpath
import os
import platform
import sys

# Define globals
__APP_AUTHOR__ = 'Liam Deacon'
__APP_COPYRIGHT__ = '\xa9'+'2013 {0}'.format(__APP_AUTHOR__)
__APP_DESCRIPTION__ = ('A simple Python-based program ' +
                      'for Viewing Elements in the periodic table')
__APP_EMAIL__ = 'liam.m.deacon@gmail.com'
__APP_LICENSE__ = 'MIT License'
__APP_NAME__ = 'Peridic Table'
__APP_VERSION__ = '0.1-alpha'
__PYTHON__ = "{0}.{1}.{2}".format(sys.version_info.major,
                                         sys.version_info.minor,
                                         sys.version_info.micro, 
                                         sys.version_info.releaselevel)

# Platform specific setup
if platform.system() is 'Windows':
    from ctypes import windll
    # Tell Windows Python is merely hosting the application (taskbar icon fix)
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(__APP_NAME__)

# Import Qt modules
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *


def determineGuiFrontend():
    """Determine which GUI toolkit to use"""
    try:
        guiFrontend = 'PySide {0}'.format(PySide.__version__)
    except NameError:
        guiFrontend = None
    
    if guiFrontend is None:
        try:
            guiFrontend = 'PyQt {0}'.format(PYQT_VERSION_STR)
        except NameError:
            guiFrontend = None
            
    if guiFrontend != None:
        return "Qt {0} (PyQt {1})".format(QtCore.qVersion(), guiFrontend)

__APP_GUI__ = determineGuiFrontend()

# Load resources & local modules
import res_rc

try:
    from modelling import elements
except ImportError:
    try:
        import elements
    except ImportError:
        sys.path.append(
            os.path.join(os.path.abspath(
                            os.path.dirname(os.path.dirname(__file__))), 'modelling'))
        import elements

import re
from collections import OrderedDict

elements_dict = OrderedDict([
('H', 'Hydrogen'), 
('He', 'Helium'), 
('Li', 'Lithium'), 
('Be', 'Beryllium'), 
('B', 'Boron'), 
('C', 'Carbon'), 
('N', 'Nitrogen'), 
('O', 'Oxygen'), 
('F', 'Fluorine'), 
('Ne', 'Neon'), 
('Na', 'Sodium'), 
('Mg', 'Magnesium'), 
('Al', 'Aluminium'), 
('Si', 'Silicon'), 
('P', 'Phosphorus'), 
('S', 'Sulfur'), 
('Cl', 'Chlorine'), 
('Ar', 'Argon'), 
('K', 'Potassium'), 
('Ca', 'Calcium'), 
('Sc', 'Scandium'), 
('Ti', 'Titanium'), 
('V', 'Vanadium'), 
('Cr', 'Chromium'), 
('Mn', 'Manganese'), 
('Fe', 'Iron'), 
('Co', 'Cobalt'), 
('Ni', 'Nickel'), 
('Cu', 'Copper'), 
('Zn', 'Zinc'), 
('Ga', 'Gallium'), 
('Ge', 'Germanium'), 
('As', 'Arsenic'), 
('Se', 'Selenium'), 
('Br', 'Bromine'), 
('Kr', 'Krypton'), 
('Rb', 'Rubidium'), 
('Sr', 'Strontium'), 
('Y', 'Yttrium'), 
('Zr', 'Zirconium'), 
('Nb', 'Niobium'), 
('Mo', 'Molybdenum'), 
('Tc', 'Technetium'), 
('Ru', 'Ruthenium'), 
('Rh', 'Rhodium'), 
('Pd', 'Palladium'), 
('Ag', 'Silver'), 
('Cd', 'Cadmium'), 
('In', 'Indium'), 
('Sn', 'Tin'), 
('Sb', 'Antimony'), 
('Te', 'Tellurium'), 
('I', 'Iodine'), 
('Xe', 'Xenon'), 
('Cs', 'Cesium'), 
('Ba', 'Barium'), 
('La', 'Lanthanum'), 
('Ce', 'Cerium'), 
('Pr', 'Praseodymium'), 
('Nd', 'Neodymium'), 
('Pm', 'Promethium'), 
('Sm', 'Samarium'), 
('Eu', 'Europium'), 
('Gd', 'Gadolinium'), 
('Tb', 'Terbium'), 
('Dy', 'Dysprosium'), 
('Ho', 'Holmium'), 
('Er', 'Erbium'), 
('Tm', 'Thulium'), 
('Yb', 'Ytterbium'), 
('Lu', 'Lutetium'), 
('Hf', 'Hafnium'), 
('Ta', 'Tantalum'), 
('W', 'Tungsten'), 
('Re', 'Rhenium'), 
('Os', 'Osmium'), 
('Ir', 'Iridium'), 
('Pt', 'Platinum'), 
('Au', 'Gold'), 
('Hg', 'Mercury'), 
('Tl', 'Thallium'), 
('Pb', 'Lead'), 
('Bi', 'Bismuth'), 
('Po', 'Polonium'), 
('At', 'Astatine'), 
('Rn', 'Radon'), 
('Fr', 'Francium'), 
('Ra', 'Radium'), 
('Ac', 'Actinium'), 
('Th', 'Thorium'), 
('Pa', 'Protactinium'), 
('U', 'Uranium'), 
('Np', 'Neptunium'), 
('Pu', 'Plutonium'), 
('Am', 'Americium'), 
('Cm', 'Curium'), 
('Bk', 'Berkelium'), 
('Cf', 'Californium'), 
('Es', 'Einsteinium'), 
('Fm', 'Fermium'), 
('Md', 'Mendelevium'), 
('No', 'Nobelium'), 
('Lr', 'Lawrencium'), 
('Rf', 'Rutherfordium'), 
('Db', 'Dubnium'), 
('Sg', 'Seaborgium'), 
('Bh', 'Bohrium'), 
('Hs', 'Hassium'), 
('Mt', 'Meitnerium'), 
('Ds', 'Darmstadtium'), 
('Rg', 'Roentgenium'), 
('Cn', 'Copernicium'), 
('Uut', 'Ununtrium'), 
('Fl', 'Flerovium'), 
('Uup', 'Ununpentium'), 
('Lv', 'Livermorium'), 
('Uus', 'Ununseptium'), 
('Uuo', 'Ununoctium'), 
])


# Create a class for our main window
class PeriodicTableDialog(QtGui.QFrame):
    """Periodic table dialog class"""
    def __init__(self, parent=None, toggle=True, element='H'):
        super(PeriodicTableDialog, self).__init__(parent)
 
        # Or more dynamically
        self.ui = uic.loadUi(os.path.join(
                                          os.path.dirname(__file__), 
                                          "PeriodicTable.ui"), 
                             self)
        self.ui.show()
        
        self.selectedElement = element  # default is Hydrogen
        
        #self.init()
        self.initUi()
    
    # Overload exit event to write configuration before exiting app
    def closeEvent(self, evnt):
        pass # print(self.selectedElement)
        

    # Setup extra UI elements
    def initUi(self):
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        # Setup slots
        
        # set defaults for each element
        for i in range(1, len(elements.ELEMENTS)):
            symbol = elements_dict.keys()[i - 1]
            element = elements.ELEMENTS[symbol]
            
            config = re.sub(r'([spdf])', r'\1<sup>', element.eleconfig)
            config = config.replace(' ', '</sup>&nbsp;') + '</sup>'
            element.description
            #eleaffin=0.0,
            #covrad=0.0, atmrad=0.0, vdwrad=0.0,
            tooltip = """
                <html>
                    <span style=" font-weight:600;">{name}</span><br/>
                    Z={protons}<br/>
                    {mass}&nbsp;amu<br/>
                    {config}<br/>
                    T<sub>melt</sub>={tmelt}&nbsp;K<br/>
                    T<sub>boil</sub>={tboil}&nbsp;K<br/>
                    &#961;={density}&nbsp;g/L<br/>
                    &#967;={eleneg}                   
                </html>""".format(protons=element.protons, name=element.name,
                                  tmelt=element.tmelt, tboil=element.tboil,
                                  config=config, mass=element.mass, 
                                  density=element.density, 
                                  eleneg=element.eleneg)
            
            eval('self.element_%i.clicked.connect(self.buttonClick)' % i)
            eval('''self.element_%i.setToolTip(tooltip)''' % i)
            
    def buttonClick(self):
        self.selectedElement = elements.ELEMENTS[elements_dict.keys().index(
                                                    self.sender().text()) + 1]
        self.ui.labelMass.setText('''<html><sup>%.1f</sup></html>''' 
                                  % float(self.selectedElement.mass))
        self.ui.labelZ.setText('''<html><sup>%s</sup></html>''' 
                                  % self.selectedElement.protons)
        self.ui.labelElement.setText('''<html><head/><body><p><span style=" 
                                        font-size:12pt;">%s</span></p></body>
                                        </html>''' 
                                        % self.selectedElement.symbol)


def main():
    # Again, this is boilerplate, it's going to be the same on
    # almost every app you write
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.join(
                                               os.path.dirname(__file__), 
                                               'res', 
                                               'periodictable.svg')
                                  )
                      )
    window = PeriodicTableDialog()
    window.show()
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
