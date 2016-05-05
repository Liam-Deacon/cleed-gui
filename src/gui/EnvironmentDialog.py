#!/usr/bin/python
# -*- coding: utf-8 -*-
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
from __future__ import unicode_literals, print_function, with_statement

from qtbackend import QtGui, QtCore, QtLoadUI
import res_rc
import os
import sys
from copy import deepcopy

import sqlite3 as lite

from appdirs import AppDirs

class EnvironmentDialog(QtGui.QDialog):
    '''
    Dialog class for updating system environment
    '''
    ENV = deepcopy(os.environ)
    
    DEFAULTS = {'CLEED_HOME': None,
                'CLEED_PHASE': AppDirs("phase", "CLEED").user_data_dir,
                'CSEARCH_LEED': 'cleed',
                'CSEARCH_RFAC': 'crfac'}
    
    def __init__(self, parent=None, model=None):
        super(EnvironmentDialog, self).__init__(parent)
        
        # set dictionary
        self.action = None
        
        # dynamically load ui
        try:
            self.ui = QtLoadUI("gui/EnvironmentDialog.ui", self)
        except IOError:
            self.ui = QtLoadUI(os.path.join(os.path.dirname(__file__), 
                                            "EnvironmentDialog.ui"), self)
        self.initUi()
        
        self.ui.show()
        
        self.env = self.DEFAULTS 
        self.environ = deepcopy(os.environ)
        
        # assign defaults if not present
        all(self.environ.__set__(key, self.DEFAULTS[key]) 
            for key in self.DEFAULTS.keys() if key not in self.environ) 
            
    def initUi(self, database=os.path.join(os.curdir, "cleed.db")):
        # Setup slots and signals
        self.ui.buttonBox.clicked[QtGui.QAbstractButton].connect(self.buttonPress)
        
        self.ui.addVariableButton.clicked.connect(self.addVariable)
        self.ui.deleteVariableButton.clicked.connect(self.deleteVariable)
        
        self.ui.showFullEnvironmentCheckBox.toggled.connect(self.showAll)
        self.ui.systemEnvironmentCheckBox.stateChanged.connect(
            lambda: sys.stderr.write("{}".format(self.ui.tableWidget.findItems(QtCore.QString("*"), QtCore.Qt.MatchWildcard))))
        
        self.ui.tableWidget.cellChanged.connect(self.updateVariable)
        self.ui.tableWidget.verticalHeader().setVisible(True)
        
        self.database = database
    
    def updateVariable(self, row, col):
        var = str(self.ui.tableWidget.verticalHeaderItem(row).text())
        value = str(self.ui.tableWidget.item(row, col).text())
        self.environ[var] = value
    
    def showAll(self, toggled):
        if toggled:
            keys = set(list(self.environ.keys()) + list(self.ENV.keys()))
        else:
            keys = set(self.environ.keys()) - set(os.environ.keys())
            
        vars = dict((k, self.environ[k]) if k in self.environ.keys() 
                    else (k, self.ENV[k]) for k in keys)
        
        headers = [str(self.ui.tableWidget.verticalHeaderItem(i).text()) 
                   for i in range(self.ui.tableWidget.rowCount())]
        
        for key in keys:
            if key not in headers:
                row = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(self.ui.tableWidget.rowCount())
                header_item = QtGui.QTableWidgetItem(str(key))
                self.ui.tableWidget.setVerticalHeaderItem(row, header_item)
                
            # update items and variable dictionary
            self.ui.tableWidget.setItem(row, 0, QtGui.QTableWidgetItem(vars[key]))
            self.vars[key] = vars[key]
                
        for key in headers:
            if key not in self.environ:
                try:
                    matches = self.ui.tableWidget.findItems(self.vars[key], 
                                                            QtCore.Qt.MatchExactly)
                    row = matches[0].row() 
                    self.ui.tableWidget.removeRow(row)
                except IndexError:
                    sys.stderr.write("Could not remove '{}' from table\n".format(key))   
                if key in self.vars:
                    self.vars.pop(key)
                continue
                
                # update items and variable dictionary
                self.ui.tableWidget.setItem(row, 0, QtGui.QTableWidgetItem(vars[key]))
                self.vars[key] = vars[key]
    
    def addVariable(self):
        new_var, ok = QtGui.QInputDialog.getText(self, "New variable...", 
                                                 "Enter Variable Name")
        
        # add new variable if not already in list
        if ok and str(new_var).upper() not in (key.upper() 
                                               for key in self.vars.keys()):
            row = self.ui.tableWidget.rowCount()
            item = QtGui.QTableWidgetItem(str(new_var))
            self.ui.tableWidget.insertRow(row)
            self.ui.tableWidget.setVerticalHeaderItem(row, item)
            self.environ[str(new_var)] = ''

    @property
    def vars(self):
        return dict((str(self.ui.tableWidget.verticalHeaderItem(row).text()), 
                     str(self.ui.tableWidget.item(row, 0).text())
                     if self.ui.tableWidget.item(row, 0) else '') 
                    for row in range(self.ui.tableWidget.rowCount()))
    
    def deleteVariable(self):
        row = self.ui.tableWidget.currentRow()
        active_var = str(self.ui.tableWidget.verticalHeaderItem(row).text())
        del_msg = "Do you want to delete environment variable '{}'?".format(active_var)
        reply = QtGui.QMessageBox.question(self, 
                                           'Message', 
                                           del_msg, 
                                           QtGui.QMessageBox.Yes, 
                                           QtGui.QMessageBox.No)

        if (reply == QtGui.QMessageBox.Yes and 
            active_var not in self.DEFAULTS.keys()):
            self.ui.tableWidget.removeRow(row)
            del(self.environ[active_var])
            print(self.environ)
        elif active_var in self.DEFAULTS.keys():
            info_msg = "Cannot delete variable '{}': read-only".format(active_var)
            QtGui.QMessageBox.information(self, 
                                          'Info', 
                                          info_msg, 
                                          QtGui.QMessageBox.Ok)

        
    
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