
"""
Enables python auto-completion for given textEdit
"""

from jedi import Script
from qtbackend import QtGui

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
        self.setCompleter(completer or QtGui.QCompleter())
        self.moveCursor(QtGui.QTextCursor.End)

    def _currentEditorLine(self):
        return self.textCursor().blockNumber()
    
    def _getEditorLine(self, i=None):
        i = self._currentEditorLine() if i is None else i
        return str(self.toPlainText()).split('\n')[i]

    def setCompleter(self, completer):
        if self.completer:
            try:
                self.disconnect(self.completer, 0, self, 0)
            except:
                pass
        if not completer:
            return

        completer.setWidget(self)
        completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer = completer
        self.connect(self.completer,
                     QtCore.SIGNAL("activated(const QString&)"), 
                     self.insertCompletion)

    def insertCompletion(self, completion):
        tc = self.textCursor()
        extra = (completion.length() -
            self.completer.completionPrefix().length())
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion.right(extra))
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
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (
            QtCore.Qt.Key_Enter,
            QtCore.Qt.Key_Return,
            QtCore.Qt.Key_Escape,
            QtCore.Qt.Key_Tab,
            QtCore.Qt.Key_Backtab):
                event.ignore()
                return

        try:
            ## has ctrl-E been pressed??
            isShortcut = (event.modifiers() == QtCore.Qt.ControlModifier and
                          event.key() == QtCore.Qt.Key_E)
            if (not self.completer or not isShortcut):
                QtGui.QTextEdit.keyPressEvent(self, event)
    
            ## ctrl or shift key on it's own??
            ctrlOrShift = event.modifiers() in (QtCore.Qt.ControlModifier ,
                    QtCore.Qt.ShiftModifier)
            if ctrlOrShift and event.text().isEmpty():
                # ctrl or shift key on it's own
                return
    
            eow = QtCore.QString("~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-=") #end of word
    
            hasModifier = ((event.modifiers() != QtCore.Qt.NoModifier) and
                            not ctrlOrShift)
            completionPrefix = str(self.textUnderCursor())
    
            if (not isShortcut and (hasModifier or str(event.text()) == '' or
                                    len(completionPrefix) < 3 or
                                    eow.contains(str(event.text())[-1]))):
                self.completer.popup().hide()
                return
    
            if (completionPrefix != self.completer.completionPrefix()):
                self.completer.setCompletionPrefix(completionPrefix)
                popup = self.completer.popup()
                popup.setCurrentIndex(
                    self.completer.completionModel().index(0,0))
    
            cr = self.cursorRect()
            cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                + self.completer.popup().verticalScrollBar().sizeHint().width())
            self.completer.complete(cr) ## popup it up!
            
        except AttributeError:
            pass

class AutoCompleter(QtGui.Completer):
    def __init__(self, parent=None, text_edit=None):
        super(AutoCompleter, self).__init__(parent)
        self.text_edit = None;
        self.setTextEdit(text_edit)
        self.update()
    
    def setTextEdit(self, textEdit):
        if textEdit is None: 
            return
        
        if self.text_edit is not None:
            # unset TextEdit here
            pass
        
    def _getCompletionDictionary(self, line):
        script = Script()
    
    def update(self):
        ''' updates to give suggestions for current line of text edit '''
        try:
            line = str(self.text_edit.toPlainText()
                   ).split('\n')[self.textCursor().blockNumber()]
        except: 
            pass
        else:
            self.setModel(QtGui.QStringListModel())
            model.setStringList(self._getCompletionDictionary(line))
        
        