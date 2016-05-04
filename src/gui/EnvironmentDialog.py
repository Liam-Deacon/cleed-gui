'''
Created on 04 May 2016

@author: Liam Deacon

@contact: liam.m.deacon@gmail.com

@copyright: Copyright 2016 Liam Deacon

@license: MIT License 

Permission is hereby granted, free of charge, to any person obtaining a copy 
of this software and associated documentation files (the "Software"), to deal 
in the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to 
do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.
'''
from PyQt4 import QtGui, uic
import res_rc
import os
import sys


class EnvironmentDialog(QtGui.QDialog):
    '''
    Dialog class for updating system environment
    '''
    ENV = os.environ
    
    DEFAULTS = {'CLEED_HOME': '',
                'CLEED_PHASE': '',
                'CSEARCH_LEED': '',
                'CSEARCH_RFAC': ''}
    
    def __init__(self, parent=None, model=None):
        super(EnvironmentDialog, self).__init__(parent)
        
        # set dictionary
        self.action = None
        
        # dynamically load ui
        try:
            self.ui = uic.loadUi("gui/EnvironmentDialog.ui", self)
        except IOError:
            self.ui = uic.loadUi(os.path.join(os.path.dirname(__file__), 
                                              "EnvironmentDialog.ui"), self)
        self.initUi()
        
        self.ui.show()
        
        self.env = self.DEFAULTS 
            
    def initUi(self):
        # Setup slots and signals
        self.ui.buttonBox.clicked[QtGui.QAbstractButton].connect(self.buttonPress)
        
        self.ui.addVariableButton.clicked.connect(lambda: sys.stderr.write("TODO\n"))
        self.ui.deleteVariableButton.clicked.connect(self.deleteVariable)
        
        self.ui.showFullEnvironmentCheckBox.stateChanged.connect(lambda: sys.stderr.write("TODO\n"))
        self.ui.systemEnvironmentCheckBox.stateChanged.connect(lambda: sys.stderr.write("TODO\n"))
        
        self.ui.tableWidget.verticalHeader().setVisible(True)
    
    def addVariable(self):
        pass
    
    def deleteVariable(self):
        active_var = self.ui.tableWidget.verticalHeaderItem(self.ui.tableWidget.currentRow()).text()
        print('TODO: delete ' + active_var)
    
    def buttonPress(self, button):
        '''Deal with user interaction of button group'''
        action = str(button.text()).lower()
        if action == 'cancel':
            # do not apply settings & close dialog
            self.action = action
            self.ui.close()
        
        elif action == 'ok':
            self.action = action 
            self.ui.close()
            
        elif action == 'restore defaults':
            self.action = action
            self._restoreDefaultEnvironment()

    def _restoreDefaultEnvironment(self):
        pass
    
    def _reloadTable(self, full=True):
        if full:
            self.ui.tableWidget


if __name__ == "__main__":
    app = QtGui.QApplication(['EnvironmentDialog Demo'])
    window = EnvironmentDialog()
    window.show()
    app.exec_()