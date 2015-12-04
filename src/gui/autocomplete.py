
"""
Enables python auto-completion for given textEdit
"""

from jedi import Script
from qtbackend import QtGui, QtCore

import sys

# optional support for enchant spell-checking
try:
    from spelltextedit import SpellTextEdit as TextEdit
except ImportError:
    sys.stderr.write('PyEnchant not installed - unable to spell check text\n')
    TextEdit = QtGui.QTextEdit


class CompletionTextEdit(TextEdit):
    def __init__(self, parent=None, completer=None):
        super(CompletionTextEdit, self).__init__(parent)
        self.setMinimumWidth(400)
        self.completer = None
        self.setCompleter(completer or AutoCompleter())
        self.moveCursor(QtGui.QTextCursor.End)
        self.setToolTip('Text editor with simple auto-completion\n\n'
                        'Use Ctrl+Space to show suggestions')

    def _updateSuggestions(self, completer):
        if not completer: 
            return
            
        source = str(self.toPlainText())
        script = Script(source, 
                        self.textCursor().blockNumber() + 1,
                        self.textCursor().columnNumber()
                        )
        try:
            model = completer.model() or QtGui.QStringListModel()
            model.setStringList([c.name for c in script.completions()])
            if completer.model() == None:
                completer.setModel(model)
        except AttributeError as e:
            sys.stderr.write(e. e.message)

    def _currentEditorLine(self):
        return self.textCursor().blockNumber()
    
    def _getEditorLine(self, i=None):
        i = self._currentEditorLine() if i is None else i
        return str(self.toPlainText()).split('\n')[i]

    def setCompleter(self, completer):
        if self.completer:
            try:
                self.disconnect(self.completer, 0, self, 0)
            except TypeError:
                pass
        if not completer:
            return

        completer.setWidget(self)
        completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer = completer
        self.completer.insertText.connect(self.insertCompletion)

    def insertCompletion(self, completion):
        tc = self.textCursor()
        extra = (len(completion) -
            len(self.completer.completionPrefix()))
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self);
        QtGui.QTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        if (self.completer and 
            self.completer.popup() and 
            self.completer.popup().isVisible() and 
            event.key() in (QtCore.Qt.Key_Enter,
                            QtCore.Qt.Key_Return,
                            QtCore.Qt.Key_Escape,
                            QtCore.Qt.Key_Tab,
                            QtCore.Qt.Key_Backtab)):
            event.ignore()
            return
        
        ## has ctrl-Space been pressed??
        isShortcut = (event.modifiers() == QtCore.Qt.ControlModifier and\
                      event.key() == QtCore.Qt.Key_Space)
        ## modifier to complete suggestion inline ctrl-e
        inline = (event.modifiers() == QtCore.Qt.ControlModifier and \
                  (event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return) )
        ## if inline completion has been chosen
        if inline:
            # set completion mode as inline
            self.completer.setCompletionMode(QtGui.QCompleter.InlineCompletion)
            completionPrefix = self.textUnderCursor()
            if (completionPrefix != self.completer.completionPrefix()):
                self.completer.setCompletionPrefix(completionPrefix)
            self.completer.complete()
            # set the current suggestion in the text box
            self.completer.insertText.emit(self.completer.currentCompletion())
            # reset the completion mode
            self.completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
            return
        if (not self.completer or not isShortcut):
            pass
            QtGui.QTextEdit.keyPressEvent(self, event)

        ## ctrl or shift key on it's own??
        ctrlOrShift = event.modifiers() in (QtCore.Qt.ControlModifier ,\
                QtCore.Qt.ShiftModifier)
        if ctrlOrShift and event.text()== '':
            # ctrl or shift key on it's own
            return

        eow = "~!@#$%^&*+{}|:\"<>?,./;'[]\\-=" #end of word

        hasModifier = ((event.modifiers() != QtCore.Qt.NoModifier) and \
                        not ctrlOrShift)

        completionPrefix = self.textUnderCursor()
        if not isShortcut :
            if self.completer.popup():
                self.completer.popup().hide()
            return

        self._updateSuggestions(self.completer)
        self.completer.setCompletionPrefix(completionPrefix)
        popup = self.completer.popup()
        popup.setCurrentIndex(
            self.completer.completionModel().index(0,0))
        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0)
            + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr) ## popup it up!


class AutoCompleter(QtGui.QCompleter):
    insertText = QtCore.pyqtSignal(str)
    
    def __init__(self, parent=None):
        super(AutoCompleter, self).__init__(parent)
        self.connect(self,
            QtCore.SIGNAL("activated(const QString&)"), self.changeCompletion)

    def changeCompletion(self, completion):
        completion = str(completion)
        if completion.find("(") != -1:
            completion = completion[:completion.find("(")]
        prefix = str(self.completionPrefix())
        if completion != prefix and len(completion) > len(prefix): 
            self.insertText.emit(completion)

class QAutoCompleter(QtGui.QCompleter):
    def __init__(self, parent=None, text_edit=None):
        super(AutoCompleter, self).__init__(parent)
        self.text_edit = None;
        self.script = None
        self.setTextEdit(text_edit)
        self._update()
    
    def setTextEdit(self, textEdit):
        if textEdit is None: 
            return
        
        if self.text_edit is not None:
            # unset TextEdit here
            pass
    
        self.text_edit = textEdit
        self.text_edit.textChanged.connect(self._update)
    
    def _textString(self):
        return str(self.text_edit.toPlainText())
    
    def _currentPos(self):
        return self.text_edit.textCursor().columnNumber()
    
    def _currentLine(self):
        return self.text_edit.textCursor().blockNumber() + 1
    
    def _currentLineText(self):
        return self._textString().split('\n')[self._currentLine()]
    
    def _getCompletionWords(self, script=None, line_no=None, col=None):
        self.script = Script(script or self._textString(), 
                             line_no or self._currentLine(), 
                             col or self._currentPos())
        return [c.name for c in self.script.completions()]
    
    def _getCompletions(self):
        return self.script.completions()
    
    def _update(self):
        ''' updates to give suggestions for current line of text edit '''
        try:
            line = self._currentLine()
        except: 
            raise
        else:
            from PyQt4 import QtGui
            self._model = QtGui.QStringListModel()
            self._model.setStringList(self._getCompletionWords())
            self.setModel(self._model)
            print(self._getCompletionWords())

if __name__ == '__main__':
    app  = QtGui.QApplication([])
    widget = CompletionTextEdit()
    widget.setCompleter(AutoCompleter(widget))
    widget.show()
    app.exec_()   
    