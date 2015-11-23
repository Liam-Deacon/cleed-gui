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
** mainwindow.py ** - provides the main window class for the CLEED GUI.
'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

# Import standard library modules
import logging
import os
import platform
import sys
from copy import deepcopy
from collections import OrderedDict

# Import Qt modules
from qtbackend import QtCore, QtGui, QtLoadUI, variant as __QT_TYPE__

# import package modules
from interceptor import OutputInterceptor
from mdichild import MdiChild
from projectexplorer import ProjectTreeWidget, ProjectItem, ModelItem

from project import Project

import res_rc  # note this requires compiled resource file res_rc.py

# other modules
#from settings import Settings
from ImportDialog import ImportDialog

# Define globals
__APP_AUTHOR__ = 'Liam Deacon'
__APP_COPYRIGHT__ = '\xa9' + '2013-2015 {0}'.format(__APP_AUTHOR__)
__APP_DESCRIPTION__ = ('CLEED - Interactive Visualiser (IV) \n '
                        '- a GUI front end to the CLEED package')
__APP_DISTRIBUTION__ = 'cleed-gui'
__APP_EMAIL__ = 'liam.deacon@diamond.ac.uk'
__APP_LICENSE__ = 'GNU General Public License 3.0'
__APP_NAME__ = u'CLEED-IV'
__APP_VERSION__ = '0.1.0-dev'
__PYTHON__ = "{0}.{1}.{2}".format(sys.version_info.major,
                                  sys.version_info.minor,
                                  sys.version_info.micro, 
                                  sys.version_info.releaselevel)
__UPDATE_URL__ = ""

__DEBUG__ = True

# Platform specific setup
if platform.system() is 'Windows':
    from ctypes import windll
    # Tell Windows Python is merely hosting the application (taskbar icon fix)
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(__APP_NAME__)
        
#==============================================================================
# BEGIN GUI WIDGET PROGRAMMING
#==============================================================================


class MainWindow(QtGui.QMainWindow):
    '''Class for main application widget'''
    
    maxRecentFiles = 10
    lastDirectory = QtGui.QDesktopServices.HomeLocation
    
    class StreamProxy(QtCore.QObject):
        # only the GUI thread is allowed to write messages in the
        # LoggerWindow, so this class acts as a proxy, passing messages
        # over Qt signal/slot for thread safety
        write_text = QtCore.pyqtSignal(str)
    
        def write(self, msg):
            msg = msg.strip()
            if msg:
                self.write_text.emit(msg)

        flush_text = QtCore.pyqtSignal()
        
        def flush(self):
            self.flush_text.emit()
    
    def __init__(self, parent=None, autoload=False):
        super(MainWindow, self).__init__(parent)
        
        # dynamically load ui
        uiFile = "MDIMainWindow.ui"  # change to desired relative ui file path
        if not os.path.isfile(uiFile):
            uiFile = os.path.join('gui', "MDIMainWindow.ui")
        self.ui = QtLoadUI(uiFile)
        
        # Note: bug where extra 'self' window is shown alongside 'self.ui'
        self.setWindowFlags(QtCore.Qt.Tool)  # shoe-horn a quiet self MainWindow
        
        self._init()
        self._initUi()
        
        if autoload:
            self.loadSession()

    def _createActions(self):
        '''
        Creates additional actions not loaded from the MainWindow.ui file
        '''
        # system tray
        self.killAllAction = QtGui.QAction(QtGui.QIcon(':/x.svg'),
                                "&Kill all processes", self, 
                                triggered=self.hide)
        
        self.minimizeAction = QtGui.QAction(QtGui.QIcon(':/minus.svg'),
                                    "Mi&nimize", self, triggered=self.hide)
        
        self.maximizeAction = QtGui.QAction(QtGui.QIcon(':/new_window.svg'),
                                            "Ma&ximize", self, 
                                            triggered=self.showMaximized)
        
        self.restoreAction = QtGui.QAction(QtGui.QIcon(':/reload.svg'),
                                           "&Restore", self,
                                           triggered=self.showNormal) 

        # MDI windows
        self.closeMdiAction = QtGui.QAction(QtGui.QIcon(":/denied.svg"),
                             "&Close", self, 
                             statusTip="Close active MDI window",
                             triggered=self.ui.mdiArea.closeActiveSubWindow)

        self.closeAllMdiAction = QtGui.QAction(QtGui.QIcon(":/denied.svg"),
                             "&Close All", self, 
                             statusTip="Close active MDI window",
                             triggered=self.ui.mdiArea.closeAllSubWindows)                             
        
        self.tileMdiAction = QtGui.QAction(
                         "&Tile", self, statusTip="Tile the windows",
                         triggered=self.ui.mdiArea.tileSubWindows)

        self.cascadeMdiAction = QtGui.QAction("&Cascade", self,
                statusTip="Cascade the windows",
                triggered=self.ui.mdiArea.cascadeSubWindows)

        self.nextMdiAction = QtGui.QAction(QtGui.QIcon(":/arrow_right.svg"),
                            "Ne&xt", self,
                            shortcut=QtGui.QKeySequence.NextChild,
                            statusTip="Move the focus to the next window",
                            triggered=self.ui.mdiArea.activateNextSubWindow)

        self.previousMdiAction = QtGui.QAction(QtGui.QIcon(":/arrow_left.svg"),
                            "Pre&vious", self,
                            shortcut=QtGui.QKeySequence.PreviousChild,
                            statusTip="Move the focus to the previous window",
                            triggered=self.ui.mdiArea.activatePreviousSubWindow)
        
        self.separatorMdiAction = QtGui.QAction(self)
        self.separatorMdiAction.setSeparator(True)

    def _createMenus(self):
        '''Creates additional menus not in ui file or alter existing'''
        self.updateWindowMenu()
        self.ui.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()
        
        # recent files
        for i in range(MainWindow.maxRecentFiles):
            try:
                self.ui.recentFilesMenu.addAction(self.ui.recentFileActions[i])
            except IndexError:
                pass
        
        # add icons to menus
        self.ui.recentFilesMenu.setIcon(QtGui.QIcon(":/clock.svg"))
        self.ui.exportMenu.setIcon(QtGui.QIcon(":/export.svg"))
        self.ui.sessionMenu.setIcon(QtGui.QIcon(":/session.svg"))
        self.ui.scriptingMenu.setIcon(QtGui.QIcon(":/cog.svg"))
        
    def _createToolBars(self):
        '''Creates custom toolbars here'''
        self.ui.graphToolBar = QtGui.QToolBar("graph")
        self.ui.modelToolBar = QtGui.QToolBar("model")
        self.ui.pymolToolBar = QtGui.QToolBar("pymol")

    def _createDocks(self):
        '''Creates and customise docks not loaded from the ui file'''
        self.setDockOptions(QtGui.QMainWindow.AnimatedDocks | 
                            QtGui.QMainWindow.AllowNestedDocks)
        
        # add scripting dock
        self.ui.dockWidgetScript = QtGui.QDockWidget("Script", self)
        self.ui.dockWidgetScript.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | 
                                           QtCore.Qt.RightDockWidgetArea | 
                                           QtCore.Qt.BottomDockWidgetArea | 
                                           QtCore.Qt.TopDockWidgetArea)  # all
        self.ui.dockWidgetScript.setObjectName('dockWidgetScript')
        from scripting import CLEEDConsoleWidget
        self.console = CLEEDConsoleWidget(self)
        self.ui.dockWidgetScript.setWidget(self.console)
        self.ui.addDockWidget(QtCore.Qt.BottomDockWidgetArea, 
                              self.ui.dockWidgetScript)

    def _createTrayIcon(self):
        '''Creates system tray icon'''
        self.ui.trayIconMenu = QtGui.QMenu()
        self.ui.trayIconMenu.addAction(self.minimizeAction)
        self.ui.trayIconMenu.addAction(self.maximizeAction)
        self.ui.trayIconMenu.addAction(self.restoreAction)
        self.ui.trayIconMenu.addSeparator()
        self.ui.trayIconMenu.addAction(self.ui.exitAction)

        self.ui.trayIcon = QtGui.QSystemTrayIcon(self.ui)
        self.ui.trayIcon.setContextMenu(self.ui.trayIconMenu)
         
        icon = self.ui.windowIcon()
        self.ui.trayIcon.setIcon(icon)
        self.ui.setWindowIcon(icon)
        self.ui.trayIcon.setToolTip("CLEED-IV")
        self.ui.trayIcon.setVisible(False)

    def _createStatusBar(self):
        '''Creates custom status bar'''
        statusBar = QtGui.QStatusBar()
        statusBar = self.statusBar()
        statusBar.showMessage("Ready")
        #statusBar.addWidget(QtGui.QLabel("test"), 1)
        #=======================================================================
        # m_statusLeft = QtGui.QLabel("Left", self)
        # m_statusLeft.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        # m_statusMiddle = QtGui.QLabel("Middle", self)
        # m_statusMiddle.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        # m_statusRight = QtGui.QLabel("Right", self)
        # m_statusRight.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        # statusBar.addPermanentWidget(m_statusLeft, 1)
        # statusBar.addPermanentWidget(m_statusMiddle, 1)
        # statusBar.addPermanentWidget(m_statusRight, 2)
        #=======================================================================

    # initialise class
    def _init(self, verbose=True):
        '''initialise logging and objects before gui''' 

        ######################################
        # APP LOGGING
        ######################################
        
        # create logger with 'spam_application'
        self.logger = logging.getLogger(__APP_NAME__)
        self.logger.setLevel(logging.DEBUG)
        
        # create file handler which logs all messages
        fh = logging.FileHandler(os.path.join(os.environ['TEMP'], __APP_NAME__ 
                + str('.log')))  # temp directory is emptied on system reboot
        formatter = logging.Formatter(
                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                         "%Y-%m-%d %H:%M:%S")
        fh.setFormatter(formatter)
        fh.setLevel(logging.INFO)  # change to taste
        
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        ch.setFormatter(formatter)
        
        # add the handlers to the logger
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)
        
        if __DEBUG__:
            pwd = os.path.dirname(__file__)
            os.system('pyrcc4 %s -o %s' % (os.path.join(pwd, 'res', 'res.qrc'),
                                           os.path.join(pwd, 'res_rc.py')))
        
        # create proxy stream layer
        stream_proxy = self.StreamProxy(self)
        stream_proxy.write_text.connect(self.write)
        stream_proxy.flush_text.connect(self.flush)
        handler = logging.StreamHandler(stream_proxy)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # intercept stdout and stderr
        sys.stderr = OutputInterceptor('stderr', sys.stderr)
        sys.stdout = OutputInterceptor('stdout', sys.stdout)
        
        # other variables
        self.projects = {}
        self.models = {}
        
    # initialise UI
    def _initUi(self):
        '''Class to initialise the Qt Widget and setup slots and signals'''

        # recent files
        self.ui.recentFileActions = []

        # Setup MDI area
        self.ui.mdiArea = QtGui.QMdiArea()
        self.ui.mdiArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.ui.mdiArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.ui.setCentralWidget(self.ui.mdiArea)
        self.ui.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.ui.windowMapper = QtCore.QSignalMapper(self)
        self.ui.windowMapper.mapped[QtGui.QWidget].connect(self.setActiveSubWindow)
        
        # setup docks
        self.ui.treeWidgetFiles = ProjectTreeWidget()
        self.ui.dockWidgetProjects.setWidget(self.ui.treeWidgetFiles)
        
        # Setup 
        self._createActions()
        self._createMenus()
        self._createToolBars()
        self._createTrayIcon()
        self._createDocks()
        self._createStatusBar()
        self.updateMenus()

        self.readSettings()

        self.setUnifiedTitleAndToolBarOnMac(True)

        # ============
        # Setup slots
        # ============
        
        # file actions
        self.ui.exitAction.triggered.connect(self.close)
        self.ui.exportXYZAction.triggered.connect(self.todo)
        self.ui.exportIVCurvesAction.triggered.connect(self.todo)
        self.ui.importAction.triggered.connect(self.importModel)
        self.ui.newAction.triggered.connect(self.newDialog)
        self.ui.openAction.triggered.connect(self.open)
        self.ui.printAction.triggered.connect(self.printer)
        for i in range(MainWindow.maxRecentFiles):
            self.ui.recentFileActions.append(
                          QtGui.QAction(self, 
                                        visible=False,
                                        triggered=self.openRecentFile)
                                          )
        self.ui.restoreSessionAction.triggered.connect(self.restoreState)
        self.ui.saveAction.triggered.connect(self.save)
        self.ui.saveAllAction.triggered.connect(self.saveAll)
        self.ui.saveAsAction.triggered.connect(self.saveAs)
        self.ui.saveSessionAction.triggered.connect(self.saveState)
        self.ui.settingsAction.triggered.connect(self.settingsDialog)
        
        # edit actions
        self.ui.copyAction.triggered.connect(self.todo)
        self.ui.cutAction.triggered.connect(self.todo)
        self.ui.pasteAction.triggered.connect(self.todo)
        self.ui.redoAction.triggered.connect(self.todo)
        self.ui.selectAllAction.triggered.connect(self.todo)
        self.ui.undoAction.triggered.connect(self.todo)
        
        # view actions
        self.ui.hideAllAction.triggered.connect(self.todo)
        self.ui.showAllAction.triggered.connect(self.todo)
        self.ui.showExplorerAction.toggled.connect(lambda x:
                            self.ui.dockWidgetProjects.setVisible(x))
        self.ui.showPropertiesAction.toggled.connect(lambda x:
                            self.ui.dockWidgetProperties.setVisible(x))
        self.ui.showLogAction.toggled.connect(lambda x:
                            self.ui.dockWidgetLog.setVisible(x))
        self.ui.showScriptAction.toggled.connect(lambda x:
                            self.ui.dockWidgetScript.setVisible(x))
        
        # process actions
        
        # window actions
        self.ui.minimiseAction.triggered.connect(self.todo)
        self.ui.closeEvent = self.closeEvent  # dodgy fix for close event
        
        # help actions
        self.ui.aboutAction.triggered.connect(self.about)
        self.ui.aboutQtAction.triggered.connect(self.aboutQt)
        self.ui.contactAction.triggered.connect(self.contactDeveloper)
        self.ui.helpAction.triggered.connect(self.help)
        self.ui.helpCleedAction.triggered.connect(self.cleedHelp)
        self.ui.updateAction.triggered.connect(self.getUpdate)
        self.ui.websiteAction.triggered.connect(self.visitWebsite)
        
        # explorer dock
        #self.ui.dockWidgetProjects.visibilityChanged.connect(self.updateDocks)
        
        # log dock
        #self.ui.dockWidgetLog.visibilityChanged.connect(self.updateDocks)
         
        # properties dock
        #self.ui.dockWidgetProperties.visibilityChanged.connect(self.updateDocks)
        
        # script dock
        if self.ui.dockWidgetScript.isVisible():
            self.console.ipyconsole.setActiveWindow()
            self.console.ipyconsole.setFocus(QtCore.Qt.ActiveWindowFocusReason)
        #self.ui.dockWidgetScript.visibilityChanged.connect(self.updateDocks)
        # main widget
        
        # systray
        self.ui.trayIcon.messageClicked.connect(self.trayMessageClicked)
        self.ui.trayIcon.activated.connect(self.trayIconActivated)
   
    def _createUndoGroup(self):
        '''Creates an Undo group for the application'''
        self.ui.undoGroup = QtGui.QUndoGroup()
    
    def shutdown(self):
        logger = logging.getLogger(__APP_NAME__)
        for handler in logger.handlers:
            logger.removeHandler(handler)

    @QtCore.pyqtSlot(str)
    def write(self, msg):
        if 'ERROR' in msg:
            color = QtGui.QColor('Red')
        elif 'WARNING' in msg:
            color = QtGui.QColor('Orange')
        elif 'INFO' in msg:
            color = QtGui.QColor('Blue')
        else:
            color = QtGui.QColor('Black')
        self.ui.textEditLog.setTextColor(color)
        self.ui.textEditLog.append(msg)
        self.ui.textEditLog.setTextColor(QtGui.QColor('Black'))
        
    @QtCore.pyqtSlot()
    def flush(self):
        if self.ui.isHidden():
            self.ui.show()
        self.ui.raise_()


    # Show about dialog
    def about(self):
        """Display 'About' dialog"""
        text = __APP_DESCRIPTION__
        text += '\n\nAuthor: {0}'.format(__APP_AUTHOR__)
        text += '\nEmail: {0}'.format(__APP_EMAIL__)
        text += '\n\nApp version: {0}'.format(__APP_VERSION__)
        text += '\n{0}'.format(__APP_COPYRIGHT__)
        text += '\n' + __APP_LICENSE__
        text += '\n\nPython: {0}'.format(__PYTHON__)
        text += '\nGUI frontend: {0} {1}'.format(__QT_TYPE__, 
                                                 QtCore.QT_VERSION_STR)

        QtGui.QMessageBox.about(self, self.ui.windowTitle(), text)
    
    # Display about dialog
    def aboutQt(self):
        """Display Qt dialog"""
        QtGui.QApplication.aboutQt()
    
    def activeMdiChild(self):
        '''Returns a handle to the active MDI child window.
        If no such handle exists then :code:py:`None` will be returned.
        '''
        try:
            return self.ui.mdiArea.activeSubWindow()
        except:
            return None
    
    def cleedHelp(self):
        '''display CLEED help in browser'''
        help_file = str((os.path.abspath(os.path.join(
                        '.', 'gui', 'res', 'help', 'html', 'index.html'))))
        if not QtGui.QDesktopServices.openUrl(
                            QtCore.QUrl.fromLocalFile(help_file)):
            self.logger.error(
                "Could not open CLEED help file '%s' in browser" % help_file)
            
    def closeEvent(self, event):
        '''override closeEvent'''
        if not self.ui.trayIcon.isVisible():
            self.ui.hide()
            self.ui.trayIcon.show()
            self.ui.trayIcon.showMessage("CLEED-IV",
                    "The program will keep running in the system tray. To "
                    "terminate the program, choose 'Exit' in the "
                    "context menu of the system tray entry.",
                    self.ui.trayIcon.Information, 25000)
            event.ignore()
        else:
            self.ui.mdiArea.closeAllSubWindows()
            if self.ui.mdiArea.currentSubWindow():
                event.ignore()
            else:
                self.writeSettings()
                event.accept()
                sys.exit(0)  # force app to exit

    # Report bug / email devs
    def contactDeveloper(self, body=""):
        '''open email client with email to developer''' 
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("mailto: "
            "{email}?cc={cc}?subject={name} feedback&body={body}"
            "".format(email=__APP_EMAIL__, 
                      name=__APP_NAME__, 
                      cc="georg.held@reading.ac.uk",
                      body=str(body))))

    def copy(self):
        '''use MDI child copy method'''
        if self.activeMdiChild():
            self.activeMdiChild().copy()
        else:
            self.todo()

    def createMdiChild(self):
        '''create new MDI child'''
        child = MdiChild()
        self.ui.mdiArea.addSubWindow(child)

        child.copyAvailable.connect(self.cutAction.setEnabled)
        child.copyAvailable.connect(self.copyAction.setEnabled)

        return child
    
    def cut(self):
        '''use MDI child cut method'''
        if self.activeMdiChild():
            self.activeMdiChild().cut()
        else:
            self.todo()
    
    @property
    def docks(self):
        docks = {}
        for dock in [child for child in self.ui.findChildren(QtGui.QDockWidget)]:
            docks[str(dock.objectName()).replace('dockWidget', 
                                                 '').lower()] = dock  
        return docks
    
    def findMdiChild(self, fileName):
        '''find mdi child'''
        canonicalFilePath = QtCore.QFileInfo(fileName).canonicalFilePath()

        for window in self.ui.mdiArea.subWindowList():
            if window.widget().currentFile() == canonicalFilePath:
                return window
        return None
    
    # check for update
    def getUpdate(self):
        """Check for app updates"""
        from UpdateDialog import UpdateDialog
        updateDialog = UpdateDialog(parent=self)
        updateDialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        updateDialog.exec_()
    
    # export model as text file
    def exportModel(self):
        '''Export model as text file'''
        pass
    
    def importDialog(self):
        '''Open dialog and radio options'''
        importDialog = ImportDialog(parent=self, 
                            model=str(self.ui.tabWidget.tabText(
                                    self.ui.tabWidget.currentIndex())).lower())
        importDialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        importDialog.finished.connect(self.parseInput)
        importDialog.exec_()
    
    # import model from text file
    def importModel(self):
        '''Import model from text file'''
        pass
    
    def importProject(self):
        '''Import a project'''
        project = QtGui.QFileDialog.getExistingDirectory(parent=self, 
                            caption="Select CLEED project directory...")
        if os.path.isdir(project) and not project in self.projects:
            self.projects.append(project)
            
         #"Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)"
    
    def loadSession(self, filename=None):
        ''' Loads a previous session '''
        # simulate loading session
        import time
        time.sleep(1)
    
    def loadFile(self, fileName):
        file = QtCore.QFile(fileName)
        if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, "Recent Files",
                    "Cannot read file %s:\n%s." % (fileName, 
                                                   file.errorString()))
            return

        instr = QtCore.QTextStream(file)
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.textEdit.setPlainText(instr.readAll())
        QtGui.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName)
        self.statusBar().showMessage("Loaded: %s" % fileName, 2000)
        
    def help(self):
        """Display help"""
        help_file = str((os.path.abspath(os.path.join(
                        '.', 'res', 'help', 'html', 'index.html'))))
        if not QtGui.QDesktopServices.openUrl(
                            QtCore.QUrl.fromLocalFile(help_file)):
            self.logger.error(
                    "Could not open help file '%s' in browser" % help_file)

    def getInputFile(self, startpath=str(os.path.expanduser('~')), model=None):
        '''returns file path of input'''
        if model == None:
            model = ''
        else:
            model += ' '
        
        model = model.capitalize()
        
        # start at last known directory
        if os.path.exists(self.lastpath):
            if os.path.isfile(self.lastpath):
                startpath = os.path.dirname(self.lastpath)
            else:
                startpath = self.lastpath
        
        filepath = str(QFileDialog.getOpenFileName(parent=None, 
                     caption='Open %sInput File' % model, directory=startpath))
        
        return filepath

    def openCLEEDManual(self):
        '''open pdf manual'''
        manual = os.path.abspath(os.path.join(
                    '.', 'gui', 'help', 'pdf', 'CLEED_manual.pdf'))
        if sys.platform.startswith('darwin'):
            success = os.system(manual)
        elif sys.platform.startswith('linux'):
            success = os.system(manual)
        elif sys.platform.startswith('win32'):
            success = os.system('start ' + manual)
            
        if not success:
            self.logger.error("Could not open pdf manual: '%s'" % manual)
    
    def newDialog(self, filename=None):
        '''Open New file dialog'''
        pass
        #self.newModel(filename)
        #self.newFile()
        #self.newInputFile(filename)
        
    def newInputFile(self, filename=None):
        '''create new MDI child window of *.inp'''
        pass
    
    def newGraphFile(self, filename=None):
        pass
    
    def newPyMolFile(self, filename=None):
        child = self.createPyMolMdiChild()
        child.newFile()
        child.show()
    
    def newFile(self, filename=None):
        child = self.createMdiChild()
        child.newFile()
        child.show()

    def open(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self)
        if fileName:
            existing = self.findMdiChild(fileName)
            if existing:
                self.ui.mdiArea.setActiveSubWindow(existing)
                return

            child = self.createMdiChild()
            if child.loadFile(fileName):
                self.statusBar().showMessage("File loaded", 2000)
                child.show()
            else:
                child.close()
    
    def openRecentFile(self):
        action = self.sender()
        if action:
            self.loadFile(action.data())
    
    def paste(self):
        '''use MDI child paste method'''
        if self.activeMdiChild():
            self.activeMdiChild().paste()
        else:
            self.todo()
    
    # check type of input file
    def parseInput(self):
        if isinstance(self.sender(), ImportDialog):
            # check user did not abort
            if self.sender().action == 'cancel':
                print('cancel') 
                return
            
            # determine file type
            if self.sender().ui.radioBulk.isChecked():
                model = 'bulk'
            else:
                model = 'slab'
        
        else:  # guess from active tab
            tabText = str(self.ui.tabWidget.tabText(
                                self.ui.tabWidget.currentIndex())).lower()
            if tabText == 'bulk' or tabText == 'slab':
                model = tabText
            else:  # unknown
                return self.importDialog()  # start dialog
        
        filename = self.getInputFile(model=model)

        if not os.path.exists(filename):
            return  # user aborted
        else:
            self.lastpath = filename
        
        try:
            pass
            
        except IOError:
            self.logger.error("IOError: Unable to open input file '%s'" 
                              % filename)
    
    def printer(self):
        '''prints MDI window'''
        if self.activeMdiChild():
            self.activeMdiChild().printer()
        else:
            self.todo()

    def printPreview(self):
        if self.activeMdiChild():
            self.activeMdiChild().printPreview()
        else:
            self.todo()
    
    @property
    def processes(self):
        import psutil 
        pid = os.getpid()
        children = psutil.Process().get_children(recursive=False)
        pids = {'main_pid': pid, 'sub_processes': children}
        return pids
    
    def readStdOutput(self):
        self.ui.textEditLog.append(str(self.readAllStandardOutput()))
    
    def save(self):
        '''save current window'''
        if self.activeMdiChild() and self.activeMdiChild().save():
            msg = "Saved file: '%s'" % self.activeMdiChild()
            self.statusBar().showMessage(msg, 2000)
            self.logger.info(msg)
        
    def saveAs(self):
        '''open saveAs dialog of MDI child''' 
        if self.activeMdiChild() and self.activeMdiChild().saveAs():
            msg = "Saved file: '%s'" % self.activeMdiChild()
            self.statusBar().showMessage(msg, 2000)
            self.logger.info(msg)
        
    def saveAll(self):
        '''save all objects'''
        if len(self.ui.mdiArea.subWindowList()) < 1:
            self.logger.warning("SaveAll aborted: No child windows")
            return
        for window in self.ui.mdiArea.subWindowList():
            if not window.save():
                msg = "Failed to save file: '%s'" % window
                self.logger.error(msg)

    def setActiveSubWindow(self, window):
        '''set active MDI child'''
        if window:
            self.ui.mdiArea.setActiveSubWindow(window)

    def setCurrentFile(self, fileName):
        '''update recent files to current file'''
        self.curFile = fileName
        if self.curFile:
            self.setWindowTitle("%s - Recent Files" 
                                % self.strippedName(self.curFile))
        else:
            self.setWindowTitle("Recent Files")

        settings = QtCore.QSettings(__APP_DISTRIBUTION__, __APP_NAME__)
        files = settings.value('recentFileList')

        try:
            files.remove(fileName)
        except ValueError:
            pass

        files.insert(0, fileName)
        del files[MainWindow.MaxRecentFiles:]

        settings.setValue('recentFileList', files)

        for widget in QtGui.QApplication.topLevelWidgets():
            if isinstance(widget, MainWindow):
                widget.updateRecentFileActions()

    def setVisible(self, visible):
        self.minimizeAction.setEnabled(visible)
        self.maximizeAction.setEnabled(not self.isMaximized())
        self.restoreAction.setEnabled(self.isMaximized() or not visible)
        super(MainWindow, self).setVisible(visible)

    def settingsDialog(self):
        """Launch settings dialog"""
        from dialogs import SettingsDialog
        settingsDialog = SettingsDialog(parent=self)
        settingsDialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        settingsDialog.finished.connect(self.updateSettings)
        settingsDialog.exec_()

    def showTrayMessage(self, msg, 
                        icon=QtGui.QSystemTrayIcon.Information, msecs=5000):
        '''display system tray message'''
        self.ui.trayIcon.showMessage(__APP_NAME__, msg, icon, msecs)
        
    def strippedName(self, fullFileName):
        '''return filename without path using QFileInfo'''
        return QtCore.QFileInfo(fullFileName).fileName()
        
    def todo(self):
        '''dummy function if not implemented'''
        self.logger.warning("'%s' is not implemented yet" % str(
                                                self.sender().objectName()))
    
    @property
    def toolbars(self):
        toolbars = {}
        for toolbar in [child for child in 
                        self.ui.findChildren(QtGui.QToolBar)]:
            toolbars[str(toolbar.objectName()).lower().replace('toolbar', 
                                                               '')] = toolbar
        return toolbars
    
    def trayIconActivated(self, reason):
        '''systray icon activated'''
        if reason == QtGui.QSystemTrayIcon.Trigger:
            self.logger.info("Systray icon triggered")
        elif reason == QtGui.QSystemTrayIcon.DoubleClick:
            self.ui.setVisible(True)
            self.ui.setWindowState(QtCore.Qt.WindowMaximized)
        elif reason == QtGui.QSystemTrayIcon.MiddleClick:
            self.logger.info("Systray icon activated by middle click")
   
    def trayMessageClicked(self):
        self.logger.debug("Tray message clicked")
    
    def readSettings(self):
        settings = QtCore.QSettings(__APP_DISTRIBUTION__, __APP_NAME__)
        
        # window geometry settings
        pos = settings.value("mainwindow/position", QtCore.QPoint(200, 200))
        size = settings.value("mainwindow/size", QtCore.QSize(400, 400))
        max = settings.value("mainwindow/maximized", False)
        self.move(pos)
        self.resize(size)
        if max:
            self.showMaximized()
            
        # dock widgets
        area = settings.value("docks/properties/area", 
                              QtCore.Qt.RightDockWidgetArea)
        geometry = settings.value("docks/properties/geometry", 
                             self.ui.dockWidgetProperties.geometry())
        self.ui.addDockWidget(area, self.ui.dockWidgetProperties)
        self.ui.dockWidgetProperties.setGeometry(geometry)
            
        if settings.value("docks/properties/visible", True):
            self.ui.dockWidgetProperties.show()
        else:
            self.ui.dockWidgetProperties.hide()
            
        if settings.value("projectsDockVisible", True):
            self.ui.dockWidgetProjects.show()
        else:
            self.ui.dockWidgetProjects.hide()
            
        if settings.value("logDockVisible", True):
            self.ui.dockWidgetLog.show()
        else:
            self.ui.dockWidgetLog.hide()
        
        # print all saved settings
        for i in settings.allKeys():
            pass
            #print(i, settings.value(i))
    
    def writeSettings(self):
        settings = QtCore.QSettings(__APP_DISTRIBUTION__, __APP_NAME__)
        
        # window geometry settings
        settings.setValue("mainwindow/position", self.ui.pos())
        settings.setValue("mainwindow/size", self.ui.size())
        settings.setValue("mainwindow/maximized", self.ui.isMaximized())
        
        # dock widgets
        settings.setValue("docks/properties/visible",  
                          self.ui.dockWidgetProperties.isVisible())
        settings.setValue("docks/properties/position", 
                          self.ui.dockWidgetProperties.pos())
        settings.setValue("docks/properties/size", 
                          self.ui.dockWidgetProperties.size())
        settings.setValue("docks/properties/floating",
                          self.ui.dockWidgetProperties.isFloating())
        settings.setValue("docks/properties/area", 
                          self.ui.dockWidgetArea(self.ui.dockWidgetProperties))
        settings.setValue("docks/properties/geometry",
                          self.ui.dockWidgetProperties.geometry())
        
        settings.setValue('projectsDockVisible', 
                          self.ui.dockWidgetProjects.isVisible())
        settings.setValue('logDockVisible', 
                          self.ui.dockWidgetLog.isVisible())
        
    def resetSettings(self):
        settings.setValue("propertiesDockVisible", False) 
        settings.setValue("projectsDockVisible", False) 
        settings.setValue("logDockVisible", False) 
    
    def updateModelUi(self, model=None):
        """Update model in gui""" 
        pass
    
    def updateRecentFileActions(self):
        '''update recent file list'''
        settings = QtCore.QSettings(__APP_DISTRIBUTION__, __APP_NAME__)
        files = settings.value('recentFileList')

        numRecentFiles = min(len(files), MainWindow.maxRecentFiles)

        for i in range(numRecentFiles):
            text = "&%d %s" % (i + 1, self.strippedName(files[i]))
            self.ui.recentFileActions[i].setText(text)
            self.ui.recentFileActions[i].setData(files[i])
            self.ui.recentFileActions[i].setVisible(True)

        for j in range(numRecentFiles, MainWindow.maxRecentFiles):
            self.ui.recentFileActions[j].setVisible(False)

        self.separatorAct.setVisible((numRecentFiles > 0))
    
    def updateMenus(self):
        hasMdiChild = (self.activeMdiChild() is not None)
        self.ui.saveAction.setEnabled(hasMdiChild)
        self.ui.saveAsAction.setEnabled(hasMdiChild)
        self.ui.pasteAction.setEnabled(hasMdiChild)
        self.closeMdiAction.setEnabled(hasMdiChild)
        self.closeAllMdiAction.setEnabled(hasMdiChild)
        self.tileMdiAction.setEnabled(hasMdiChild)
        self.cascadeMdiAction.setEnabled(hasMdiChild)
        self.nextMdiAction.setEnabled(hasMdiChild)
        self.previousMdiAction.setEnabled(hasMdiChild)
        self.separatorMdiAction.setVisible(hasMdiChild)

        hasSelection = (self.activeMdiChild() is not None and
                        self.activeMdiChild().textCursor().hasSelection())
        self.ui.cutAction.setEnabled(hasSelection)
        self.ui.copyAction.setEnabled(hasSelection)

    def updateWindowMenu(self):
        self.ui.windowMenu.clear()
        self.ui.windowMenu.addAction(self.closeMdiAction)
        self.ui.windowMenu.addAction(self.closeAllMdiAction)
        self.ui.windowMenu.addSeparator()
        self.ui.windowMenu.addAction(self.tileMdiAction)
        self.ui.windowMenu.addAction(self.cascadeMdiAction)
        self.ui.windowMenu.addSeparator()
        self.ui.windowMenu.addAction(self.nextMdiAction)
        self.ui.windowMenu.addAction(self.previousMdiAction)
        self.ui.windowMenu.addAction(self.separatorMdiAction)

        windows = self.ui.mdiArea.subWindowList()
        self.separatorMdiAction.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.userFriendlyCurrentFile())
            if i < 9:
                text = '&' + text

            action = self.ui.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.activeMdiChild())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)
    
    def updateSettings(self):
        '''update the application settings'''
        self.settings = self.sender().settings
        print(self.settings.__dict__)
        
    def visitWebsite(self):
        '''open link to CLEED website'''
        self.todo()
    
    def updateDocks(self):
        docks = self.docks 
        docks = [docks[dock] for dock in docks]
        
        found = {}
        for dock in docks:
            found[dock] = dock.isVisible()
        for dock in docks:
            for item in docks:
                if dock in self.ui.tabifiedDockWidgets(item):
                    found[dock] = True
                    
        # set checked state of menus
        self.ui.showExplorerAction.setChecked(found[self.ui.dockWidgetProjects])
        self.ui.showLogAction.setChecked(found[self.ui.dockWidgetLog])
        self.ui.showPropertiesAction.setChecked(found[self.ui.dockWidgetProjects])
        self.ui.showScriptAction.setChecked(found[self.ui.dockWidgetScript])
            
            
            
# boilerplate function - should be applicable to most applications
def main(argv=None):
    '''Entry point if executing as standalone''' 
    if argv is None:
        argv = sys.argv
    
    app = QtGui.QApplication(argv)
    app.processEvents()
    pixmap = QtGui.QPixmap(os.path.abspath(
                               os.path.join("res", "CLEED_logo.png")))
    splash = QtGui.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
    #splash.setMask(pixmap.mask())  # this is useful if splash isn't a rectangle
    
    # set font
    font = QtGui.QFont()
    font.setPointSize(16)
    font.setWeight(800)

    splash.setFont(font)
    
    splash.showMessage((u'Starting %s...' % __APP_NAME__), 
                       QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom, 
                       QtCore.Qt.blue)
    splash.show()

    # make sure Qt really display the splash screen 
    app.processEvents()

    app.setQuitOnLastWindowClosed(False)
    
    window = MainWindow()
    window.hide()
    
    app.setWindowIcon(window.ui.windowIcon())
    
    if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        window.logger.warning("Unable to create a Systray on this system")
    
    splash.showMessage(u'Loading session...', 
                       QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom, 
                       QtCore.Qt.blue)
    
    window.loadSession()
    
    # now kill the splash screen
    splash.finish(window)
    splash.close()
    
    if '-q' not in argv and '--quiet' not in argv:  
        window.ui.show()
    sys.exit(app.exec_())

# Execute main function if running as standalone module
if __name__ == '__main__':
    main()
