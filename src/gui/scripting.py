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

import os
import sys

# Set the QT API to PyQt4
from qtbackend import QtGui, QtCore

# Import the console machinery from ipython
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport

from highlighter import PythonHighlighter
from autocomplete import AutoCompleter, CompletionTextEdit


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


class DictionaryCompleter(QtGui.QCompleter):
    def __init__(self, parent=None):
        words = []
        try:
            f = open("/usr/share/dict/words","r")
            for word in f:
                words.append(word.strip())
            f.close()
        except IOError:
            print("dictionary not in anticipated location")
        QtGui.QCompleter.__init__(self, words, parent)
 
 
class LineTextWidget(QtGui.QFrame):
    class NumberBar(QtGui.QWidget):
        def __init__(self, *args):
            QtGui.QWidget.__init__(self, *args)
            self.edit = None
            # This is used to update the width of the control.
            # It is the highest line that is currently visibile.
            self.highest_line = 0
 
        def setTextEdit(self, edit):
            self.edit = edit
 
        def update(self, *args):
            '''
            Updates the number bar to display the current set of numbers.
            Also, adjusts the width of the number bar if necessary.
            '''
            # The + 4 is used to compensate for the current line being bold.
            width = self.fontMetrics().width(str(self.highest_line)) + 4
            if self.width() != width:
                self.setFixedWidth(width)
            QtGui.QWidget.update(self, *args)
 
        def paintEvent(self, event):
            contents_y = self.edit.verticalScrollBar().value()
            page_bottom = contents_y + self.edit.viewport().height()
            font_metrics = self.fontMetrics()
            current_block = self.edit.document().findBlock(
                                    self.edit.textCursor().position())
 
            painter = QtGui.QPainter(self)
 
            line_count = 0
            # Iterate over all text blocks in the document.
            block = self.edit.document().begin()
            while block.isValid():
                line_count += 1
 
                # The top left position of the block in the document
                position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()
 
                # Check if the position of the block is out side of the visible
                # area.
                if position.y() > page_bottom:
                    break
 
                # We want the line number for the selected line to be bold.
                bold = False
                if block == current_block:
                    bold = True
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
 
                # Draw the line number right justified at the y position of the
                # line. 3 is a magic padding number. drawText(x, y, text).
                painter.drawText(self.width() - 
                    font_metrics.width(str(line_count)) - 3, 
                        round(position.y()) - contents_y + font_metrics.ascent(), 
                            str(line_count))
 
                # Remove the bold style if it was set previously.
                if bold:
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)
 
                block = block.next()
 
            self.highest_line = line_count
            painter.end()
 
            QtGui.QWidget.paintEvent(self, event)
 
 
    def __init__(self, edit=None, *args):
        QtGui.QFrame.__init__(self, *args)
 
        self.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken)
 
        self.edit = edit or QtGui.QTextEdit()
        self.edit.setFrameStyle(QtGui.QFrame.NoFrame)
        try:
            self.edit.setAcceptRichText(False)
        except AttributeError:
            pass
            
        self.number_bar = self.NumberBar()
        self.number_bar.setTextEdit(self.edit)
 
        hbox = QtGui.QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setMargin(0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(self.edit)
 
        self.edit.installEventFilter(self)
        self.edit.viewport().installEventFilter(self)
 
    def eventFilter(self, object, event):
        # Update the line numbers for all events on the text edit and the viewport.
        # This is easier than connecting all necessary singals.
        if object in (self.edit, self.edit.viewport()):
            self.number_bar.update()
            return False
        return QtGui.QFrame.eventFilter(object, event)
 
    def getTextEdit(self):
        return self.edit


class PythonTextEdit(CompletionTextEdit):
    """
    TextEdit widget for writing Python code
    """
    def __init__(self, parent=None):
        super(PythonTextEdit, self).__init__(parent)
        self.highlighter = PythonHighlighter(self.document())


class CLEEDConsoleWidget(QtGui.QWidget):
    """ 
    Customised IPython widget for CLEED. 
    """
    
    lastpath = os.path.expanduser(os.path.join('~', 'script.py'))
    
    def __init__(self, parent=None):
        super(CLEEDConsoleWidget, self).__init__(parent)
        layout = QtGui.QVBoxLayout(self)
        edit_layout = QtGui.QVBoxLayout()
        button_layout = QtGui.QHBoxLayout()
        
        self.ipyConsole = QIPythonWidget(customBanner=
            "*** Welcome to the CLEED embedded IPython console ***\n\n")
        
        self.tabWidget = QtGui.QTabWidget()
        layout.addWidget(self.tabWidget)
        
        self.save_button = QtGui.QPushButton('Save')
        self.load_button = QtGui.QPushButton('Load')
        self.run_button = QtGui.QPushButton('Run...')
        
        self.run_button.pressed.connect(self._run)
        self.save_button.pressed.connect(self._save)
        self.load_button.pressed.connect(self._load)
        
        try:
            import res_rc
            self.save_button.setIcon(QtGui.QIcon('res/save.svg'))
            self.load_button.setIcon(QtGui.QIcon('res/folder_fill.svg'))
            self.run_button.setIcon(QtGui.QIcon('res/play.svg'))
        except:
            pass
        
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.run_button)
        
        self.lineTextWidget = LineTextWidget(edit=PythonTextEdit()) 
        self.scriptEdit = self.lineTextWidget.getTextEdit() 
        edit_layout.addWidget(self.lineTextWidget)
        edit_layout.addLayout(button_layout)
        
        edit_widget = QtGui.QWidget()
        edit_widget.setLayout(edit_layout)
        
        self.scriptEdit.setFrameStyle(QtGui.QFrame.Panel | 
                                      QtGui.QFrame.Sunken)
        
        self.tabWidget.addTab(self.ipyConsole, 'Console')
        self.tabWidget.addTab(edit_widget, 'Editor')
        
        self.scriptEdit.textChanged.connect(lambda:  
                    self.tabWidget.setTabText(1, "{} *".format(
                        str(self.tabWidget.tabText(1)).rstrip(' *')) 
                                if str(self.scriptEdit.toPlainText()) != ''
                                else 'Editor'))
        #from PyQt4 import QtGui, QtCore
        save_action = QtGui.QAction(QtGui.QIcon("res/save.svg"), 
                                    "&Save", 
                                    self.scriptEdit,
                                    shortcut="Ctrl+S",
                                    triggered=lambda: self._save())
        load_action = QtGui.QAction(QtGui.QIcon("res/folder_fill.svg"), 
                                    "&Load", 
                                    self.scriptEdit,
                                    shortcut="Ctrl+O",
                                    triggered=lambda: self._load())
        run_action = QtGui.QAction(QtGui.QIcon("res/play.svg"), 
                                   "&Run", 
                                   self.scriptEdit,
                                   shortcut="Ctrl+R",
                                   triggered=lambda: self._run())
        
        # doesn't work on scriptEdit tab!?
        switch = lambda: self.tabWidget.setCurrentIndex(0)
                            #self.tabWidget.currentIndex()+1 % 2) 
        
        switch_action = QtGui.QAction(QtGui.QIcon('res/link.svg'),
                                      "S&witch",
                                      self.scriptEdit,
                                      shortcut="Ctrl+E",
                                      triggered=switch
                                      )
        
        self.scriptEdit.addAction(save_action)
        self.scriptEdit.addAction(load_action)
        self.scriptEdit.addAction(run_action)
        self.scriptEdit.addAction(switch_action)

        switch = lambda: self.tabWidget.setCurrentIndex(1)
        
        self.tabWidget.currentChanged.connect(lambda x: 
                self.scriptEdit.setFocus() if x == 1 
                else self.ipyConsole._control.setFocus())
        
        switch_action = QtGui.QAction(QtGui.QIcon('res/link.svg'),
                                      "S&witch",
                                      self.scriptEdit,
                                      shortcut="Ctrl+E",
                                      triggered=switch
                                      )
        
        self.ipyConsole.addAction(switch_action)
        
        self.ipyConsole.pushVariables(
            {"app": self.parent() or self,
             "console": self.ipyConsole
             })
        self.ipyConsole.printText("The application handle variable 'app' " 
                                  "is available. "
                                  "Use the 'whos' command for information on " 
                                  "available variables.")
        self.setToolTip("CLEED scripting console. \n\n"
                        "Note: type 'whos' for list of variables "
                        "or help($var) for help")
        
        # initialise with specific modules loaded
        self.ipyConsole._execute("from __future__ import "
                                 "division, unicode_literals",
                                 hidden=True)
        
        self.tabWidget.setTabText(1, "{}".format(
                        str(self.tabWidget.tabText(1)).rstrip(' *')))
        
        # default is to focus control on IPython input
        self.ipyConsole._control.setFocus()
        
#         from IPython.qt.console.completion_lexer import CompletionLexer
#         from pygments.lexers.python import PythonLexer
#         
#         self.scriptEdit.lexer = CompletionLexer(PythonLexer())
#         
#         self.scriptEdit.completer = QtGui.QCompleter()
#         
#         completer = self.scriptEdit.completer
#         completer.setWidget(self.scriptEdit)
#         completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
#         #completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
# 
#         self.scriptEdit.textChanged.connect(self._updateAutoCompleter)
#     
#     def _updateAutoCompleter(self):
#         self.scriptEdit.model = QtGui.QStringListModel()
#         line = self._currentEditorLine()
#         self.scriptEdit.completer.setModel(self.scriptEdit.model)
#         print(
#                             self.scriptEdit.lexer.get_context(line or '') or [])
    
    def _run(self):
        self.tabWidget.setCurrentIndex(0)
        script_name = str(self.tabWidget.tabText(1
                            )).rstrip(' *').lstrip('Editor')
        if script_name.startswith('(') and script_name.endswith(')'):
            script_name = script_name[1:-1]
        self.ipyConsole.printText('Executing {}...'
                                  ''.format("'" + script_name + "'" 
                                            if script_name != ''
                                            else 'custom script'))
        self.ipyConsole._execute(str(
                self.scriptEdit.toPlainText()).rstrip('\n'), False)
        
    def _load(self):
        filters = ['Python Script (*.py)',
                   'Text File (*.txt)', 
                   'All Files (*)']
        filename = str(QtGui.QFileDialog.getOpenFileName(parent=None, 
                                          caption='Open Script', 
                                          directory=self.lastpath,
                                          filter=';;'.join(filters)
                                          ))
        
        if not filename: return  # user cancelled
        
        try:
            with open(filename, 'r') as f:
                self.scriptEdit.setPlainText(''.join(f.readlines()))
                basename = os.path.basename(filename)
                self.tabWidget.setTabText(1, 'Editor ({})'.format(basename))
                self.lastpath = filename
                
        except any as e:
            err = QtGui.QErrorMessage(parent=self)
            err.showMessage("Failed to open '{}' \n\n({})"
                            "".format(filename, e.msg))
            
    
    def _save(self):
        filters = ['Python Script (*.py)',
                   'Text File (*.txt)', 
                   'All Files (*)']
        filename = str(QtGui.QFileDialog.getSaveFileName(self, 
                                          caption='Save script', 
                                          directory=self.lastpath,
                                          filter=';;'.join(filters)
                                          ))
        if not filename: return  # user cancelled
        
        try:
            with open(filename, 'w') as f:
                f.write(self.scriptEdit.toPlainText())
                basename = os.path.basename(filename)
                self.tabWidget.setTabText(1, 'Editor ({})'.format(basename))
                self.lastpath = filename
                
        except IOError as e:
            err = QtGui.QErrorMessage(parent=self)
            err.showMessage("Failed to write script {} {}"
                            "".format("to \'" + filename  + "'" 
                                      if filename else '', 
                                      '\n\n' + e.message 
                                      if e.message != ''else ''))
        

def main():
    app  = QtGui.QApplication([])
    widget = CLEEDConsoleWidget()
    widget.show()
    app.exec_()    

if __name__ == '__main__':
    main()