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
"""
**ipython.py** - defines IPython embbedded console widgets for Qt.  

Warning
-------
May require some manipulation of the IPython modules to prevent an ImportError.
For instance under certain environments the line 
:code:`from IPython.external.path import path` in `IPython.utils.text.py` 
may need to be changed to:: 
    from IPython.external.path._path import path

"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

# Set the QT API to PyQt4
from qtbackend import QtGui

# Import the console machinery from ipython
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport


class QIPythonWidget(RichIPythonWidget):
    """ 
    Convenience class for a live IPython console widget. 
    We can replace the standard banner using the customBanner argument
    """
    def __init__(self, customBanner=None, *args, **kwargs):
        if customBanner != None: 
            self.banner=customBanner
        super(QIPythonWidget, self).__init__(*args, **kwargs)
        self.kernel_manager = kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        kernel_manager.kernel.gui = 'qt4'
        self.kernel_client = kernel_client = self._kernel_manager.client()
        kernel_client.start_channels()

        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            guisupport.get_app_qt4().exit()            
        self.exit_requested.connect(stop)

    def pushVariables(self,variableDict):
        """ 
        Given a dictionary containing name / value pairs, 
        push those variables to the IPython console widget 
        """
        self.kernel_manager.kernel.shell.push(variableDict)
        
    def clearTerminal(self):
        """ Clears the terminal """
        self._control.clear()    
        
    def printText(self,text):
        """ Prints some plain text to the console """
        self._append_plain_text(text)   
             
    def executeCommand(self,command):
        """ Execute a command in the frame of the console widget """
        self._execute(command,False)


class CLEEDConsoleWidget(QtGui.QWidget):
    """ 
    Customised IPython widget for CLEED. 
    """
    def __init__(self, parent=None):
        super(CLEEDConsoleWidget, self).__init__(parent)
        layout = QtGui.QVBoxLayout(self)
        edit_layout = QtGui.QVBoxLayout()
        button_layout = QtGui.QHBoxLayout()
        
        self.ipyConsole = QIPythonWidget(customBanner=
            "*** Welcome to the CLEED embedded IPython console ***\n\n")
        
        self.tabWidget = QtGui.QTabWidget()
        layout.addWidget(self.tabWidget)

        from highlighter import PythonHighlighter
        
        self.save_button = QtGui.QPushButton('Save')
        self.load_button = QtGui.QPushButton('Load')
        self.run_button = QtGui.QPushButton('Run...')
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.run_button)
        
        self.scriptEdit = QtGui.QPlainTextEdit()
        self.highlighter = PythonHighlighter(self.scriptEdit.document())
        edit_layout.addWidget(self.scriptEdit)
        edit_layout.addLayout(button_layout)
        
        edit_widget = QtGui.QWidget()
        edit_widget.setLayout(edit_layout)
        
        self.tabWidget.addTab(self.ipyConsole, 'Console')
        self.tabWidget.addTab(edit_widget, 'Editor')
        
        self.ipyConsole.pushVariables(
            {"app": self.parent(),
             "console": self.ipyConsole
             })
        self.ipyConsole.printText("The application handle variable 'app' " 
                                  "is available. "
                                  "Use the 'whos' command for information on " 
                                  "available variables.")
        self.setToolTip("CLEED scripting console. \n\n"
                        "Note: type 'whos' for list of variables "
                        "or help($var) for help")
        

def main():
    app  = QtGui.QApplication([])
    widget = CLEEDConsoleWidget()
    widget.show()
    app.exec_()    

if __name__ == '__main__':
    main()