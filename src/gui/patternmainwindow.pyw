##############################################################################
# Author: Liam Deacon                                                        #
#                                                                            #
# Contact: liam.m.deacon@gmail.com                                           #
#                                                                            #
# Copyright: Copyright (C) 2014-2016 Liam Deacon                             #
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
** patternmainwindow.py ** - provides the main window class for LEED Pattern GUI.
'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

import os

# Import Qt modules
from qtbackend import QtCore, QtGui, QtLoadUI, variant as __QT_TYPE__

# import package modules
import res_rc  # note this requires compiled resource file res_rc.py

class MainWindow(QtGui.QMainWindow):
    '''Class for main application widget'''
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        # dynamically load ui
        uiFile = "PatternMainWindow.ui"  # change to desired relative ui file path
        if not os.path.isfile(uiFile):
            uiFile = os.path.join('gui', "MDIMainWindow.ui")
        self.ui = QtLoadUI(uiFile)
        
        # Note: bug where extra 'self' window is shown alongside 'self.ui'
        self.setWindowFlags(QtCore.Qt.Tool)  # shoe-horn a quiet self MainWindow
        
        self._init_ui()
        
    def _init_ui(self):
        # fix ui
        from patternWidget import PatternWidget
        self.pattern = PatternWidget()
        self.ui.setCentralWidget(self.pattern)
        
        # create stuff
        self._createActions()
        self._createToolbars()
        
    def _createActions(self):
        pass
    
    def _createToolbars(self):
        pass
    
    def _todo(self):
        QtGui.QMessageBox.information(self, "Information", "Not implemented... yet!")
        
    
if __name__ == "__main__":
    import sys
    
    # launch application
    app = QtGui.QApplication(sys.argv)
    
    window = MainWindow()
    window.ui.show()
    
    sys.exit(app.exec_())