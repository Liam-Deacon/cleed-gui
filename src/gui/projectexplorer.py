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

'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

from PyQt4 import QtGui
from PyQt4.QtGui import QLineEdit, QDialog
from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QIcon, QFileDialog
from PyQt4.QtCore import QFileInfo, Qt

import os.path
try:
    import res_rc
except:
    pass

class ProjectTreeWidget(QTreeWidget):
    def __init__(self):
        QTreeWidget.__init__(self)
        
        self.setColumnCount(1)
        self.setHeaderLabel("Projects")
        
        # explorer actions       
        self.renameAction = QtGui.QAction(QtGui.QIcon(":/tag_stroke.svg"),
                                          "&Rename", self,
                                          triggered=self.rename)
        self.renameAction.setToolTip("Rename project...")
        
        self.refreshAction = QtGui.QAction(QtGui.QIcon(":/spin.svg"),
                                           "Refresh", self,
                                           triggered=self.refresh,
                                           shortcut="F5")
        self.refreshAction.setToolTip("Refresh")
         
        self.newProjectAction = QtGui.QAction(
                                      QtGui.QIcon(":/document_alt_stroke.svg"),
                                      "&New Project", self,
                                      triggered=self.newProject)
        self.newProjectAction.setToolTip("Create new project...")
        
        self.importProjectAction = QtGui.QAction(QtGui.QIcon(":/import.svg"),
                                                 "&Import Project", self,
                                                 triggered=self.importProject)
        self.importProjectAction.setToolTip("Import existing project...")    
        
        self.newModelAction = QtGui.QAction(QtGui.QIcon(":/atoms.svg"),
                                            "&New Model", self,
                                            triggered=self.newModel)
        self.newModelAction.setToolTip("Create new model...")
        
        self.importModelAction = QtGui.QAction(QtGui.QIcon(":/import.svg"),
                                               "&Import Model", self,
                                               triggered=self.importModel)
        self.importModelAction.setToolTip("Import existing model...") 
        
        self.removeProjectAction = QtGui.QAction(QtGui.QIcon(":/x.svg"),
                                                 "&Remove Project", self,
                                                 triggered=self.removeProject,
                                                 shortcut='Del')
        self.newProjectAction.setToolTip("Remove project")
        
        self.removeProjectAction = QtGui.QAction(
                                        QtGui.QIcon(":/folder_fill.svg"),
                                        "Open Project &Location", self,
                                        triggered=self.removeProject)
        self.newProjectAction.setToolTip("Opens project location in file explorer")
        
        # explorer menus
        self.explorerDefaultMenu = QtGui.QMenu()
        self.explorerDefaultMenu.addAction(self.newProjectAction)
        self.explorerDefaultMenu.addAction(self.importProjectAction)
        self.explorerDefaultMenu.addSeparator()
        #self.explorerDefaultMenu.addAction(self.copyAction)
        #self.explorerDefaultMenu.addAction(self.cutAction)
        #self.explorerDefaultMenu.addAction(self.pasteAction)
        self.explorerDefaultMenu.addAction(self.renameAction)
        self.explorerDefaultMenu.addSeparator()
        self.explorerDefaultMenu.addAction(self.refreshAction)
        
        self.explorerProjectMenu = QtGui.QMenu()
        self.explorerProjectMenu.addAction(self.newModelAction)
        self.explorerProjectMenu.addAction(self.importModelAction)
        #self.explorerProjectMenu.addSeparator()
        #self.explorerProjectMenu.addAction(self.copyAction)
        #self.explorerProjectMenu.addAction(self.cutAction)
        #self.explorerProjectMenu.addAction(self.pasteAction)
        self.explorerProjectMenu.addAction(self.renameAction)
        self.explorerProjectMenu.addAction(self.removeProjectAction)
        self.explorerProjectMenu.addSeparator()
        self.explorerProjectMenu.addAction(self.refreshAction)
        
        self.explorerFileMenu = QtGui.QMenu()
        #self.explorerFileMenu.addAction(self.newAction)
        self.explorerFileMenu.addAction(self.refreshAction) 
        
        #setup signals and slots
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.explorerPopupMenu)
        
        item = QTreeWidgetItem(self, ["parent"])
        self.addTopLevelItem(item.addChild(QTreeWidgetItem(item, ["child"])))
        self.addTopLevelItem(QTreeWidgetItem(self, ["blah"]))
        
        #recent projects
        self.recent_projects = []
    
    def explorerPopupMenu(self, point):
        '''popup menu for explorer widget'''
        index = self.indexAt(point)
        if index.isValid():
            # show custom menu for file type held at given index
            item = self.itemFromIndex(index)
            if self.indexOfTopLevelItem(item) > -1:
                # then its a top-level item
                self.selectionModel().setCurrentIndex(index, 
                                            QtGui.QItemSelectionModel.NoUpdate)
                self.explorerProjectMenu.popup(
                        self.viewport().mapToGlobal(point))
            else:
                self.explorerFileMenu.popup(
                        self.viewport().mapToGlobal(point))
                print('another item: %s' % item.text(0))
        else:
            # provide default menu
            self.explorerDefaultMenu.popup(
                        self.viewport().mapToGlobal(point))
    
    def currentProject(self):
        '''returns the currently selected project'''
        item = QTreeWidgetItem  # added for auto-complete in PyDev
        item = self.currentItem()
        
        # get root item
        while self.indexOfTopLevelItem(item) < 0:
            item = item.parent()

        return {'name': item.text(self.currentColumn()), 'item': item}
    
    def newProject(self, projectName=None):
        if not projectName:
            projectName = "Untitled_Project"
        
        # get storage location for project
        homePath = QtGui.QDesktopServices.storageLocation(
                                        QtGui.QDesktopServices.HomeLocation)
        projectDir = os.path.join(homePath, "CLEED", "models")
        folder = QFileDialog.getExistingDirectory(parent=self, 
                            caption="Select Project Base Directory",
                            directory=projectDir, 
                            options=QFileDialog.ShowDirsOnly | 
                                    QFileDialog.DontResolveSymlinks)    
        if folder:
            # do stuff
            items = [self.treeWidgetFiles.topLevelItem(i).Path for i 
                     in range(self.treeWidgetFiles.topLevelItemCount())]
            if folder not in items:
                proj = ProjectItem(self.ui.treeWidgetFiles, path=folder)
            else:
                pass
                self.treeWidgetFiles.setCurrentIndex(0, items.index(folder, ))
    
    def newModel(self, project, modelName=None):
        if not modelName:
            text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 
                                              'Enter model name:')
            if not ok:
                return
            
            modelName = text
        
        try:
            index = self.selectedIndexes()[0]
            parent = self.itemFromIndex(index)
            path = os.path.join(parent.Path, modelName)
             
            if not modelName:
                modelName = "New_Model"
                i = 1
                path = os.path.join(parent.Path, modelName)
                while os.path.isdir(modelName):
                    modelName = "New_Model%i" % i
                    path = os.path.join(parent.Path, modelName)
                    i += 1
            
            model = ModelItem(path)
            a = parent.addChild(model)
            print(a)    
            if not os.path.exists(path):
                os.makedirs(path, 755)
                # add new input files
                
            else:
                pass
        
        except IndexError:
            # no index selected (or created?)
            pass    
    
    def importModel(self):
        '''Import model from text file'''
        pass
    
    def importProject(self):
        '''Import a project'''
        project = QtGui.QFileDialog.getExistingDirectory(parent=self, 
                            caption="Select CLEED project directory...")
        if os.path.isdir(project) and not project in self.projects:
            self.projects.append(project)
    
    def removeProject(self):
        print(self.treeWidgetFiles.getCurrentIndex())
        self.todo()
    
    def rename(self):
        '''Renames current project'''
        project = self.currentProject()
        old_name = project['name']
        new_name, ok = QtGui.QInputDialog.getText(self, 
                                                  self.tr("Rename Project"),
                                                  self.tr("New name:"), 
                                                  QLineEdit.Normal,
                                                  old_name)
        if ok and new_name is not old_name:
            item = QTreeWidgetItem
            item = project['item']
            item.setText(self.currentColumn(), new_name) 
        
        
    def refresh(self):
        self.todo()
    
    def getChildItemsDict(self, obj):
        try:
            if isinstance(obj, QTreeWidget):
                root = obj.invisibleRootItem()
            elif isinstance(obj, QTreeWidgetItem):
                root = obj
            child_count = root.childCount()
            topLevelDict = {}
            for i in range(child_count):
                item = root.child(i)
                var = str(item.text(0))
                exec('%s = i' % var)
                topLevelDict.update({var: eval(var)})
            return topLevelDict
        except any as e:
            self.logger.error(e.msg)
            
    def getChildItemHandle(self, obj, name=str):
        if isinstance(obj, QTreeWidget):
            root = obj.invisibleRootItem()
        elif isinstance(obj, QTreeWidgetItem):
            root = obj
        
        if isinstance(name, int):
            return root.child(name)
        elif isinstance(name, str):
            for i in range(root.childCount()):
                item = root.child(i)
                if str(item.text(0)) == name:
                    return item 

class ProjectItem(QTreeWidgetItem):
    '''class for project items'''
    def __init__(self, parent=None, path=None):
        super(ProjectItem, self).__init__(parent)
        self.setProjectPath(path)
        self.setIcon(0, QIcon(":/folder_fill.svg"))
        self.name = "New_Project"
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setProjectPath(path)
        
        #add children
        self._init_children()
    
    def _init_children(self):
        self.addChild()
    
    @property
    def project_path(self):
        return self._path
    
    @project_path.setter
    def project_path(self, path):
        self._path = path
    
    def setProjectPath(self, path):
        self.Path = path
        self.Name = QFileInfo(path).baseName()
        self.setText(0, self.Name)
        self.setToolTip(0, path)
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name
    
        
class ModelItem(QTreeWidgetItem):
    '''class for project items'''
    def __init__(self, parent=None, path=None):
        super(ModelItem, self).__init__(parent)
        self.setModelName(path)
        self.setIcon(0, QIcon(":/atoms.svg"))
        self.name = "New_Model"
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setModelName(path)
    
    def setModelName(self, path):
        self.Path = path
        self.Name = QFileInfo(path).baseName()
        self.setText(0, self.Name)
        self.setToolTip(0, path)


class InputItem(QTreeWidgetItem):
    '''class for project items'''
    def __init__(self, parent=None, path=None):
        super(InputItem, self).__init__(parent)
        self.setModelName(path)
        self.setIcon(0, QIcon(":/atoms.svg"))
        self.Name = "New_Model"
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setModelName(path)
    
    def setModelName(self, path):
        self.Path = path
        self.Name = QFileInfo(path).baseName()
        self.setText(0, self.Name)
        self.setToolTip(0, path)

      
class BulkItem(QTreeWidgetItem):
    '''class for project items'''
    def __init__(self, parent=None, path=None):
        super(InputItem, self).__init__(parent)
        self.setModelName(path)
        self.setIcon(0, QIcon(":/atoms.svg"))
        self.Name = "New_Model"
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setModelName(path)
    
    def setModelName(self, path):
        self.Path = path
        self.setText(0, 'Bulk')
        self.setToolTip(0, path)

class SearchItem(QTreeWidgetItem):
    '''class for LEED-IV control items'''
    def __init__(self, parent=None, path=None):
        #super(InputItem, self).__init__(parent)
        self.setIcon(0, QIcon(":/cog.svg"))
        self.setFlags(self.flags() | Qt.ItemIsEditable)

class SettingsItem(QTreeWidgetItem):
    '''class for local settings'''
    def __init__(self, parent=None, path=None):
        #super(InputItem, self).__init__(parent)
        self.setIcon(0, QIcon(":/wrench.svg"))
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        
class IVGroupItem(QTreeWidgetItem):
    '''class for handling LEED-IV curves'''
    def __init__(self, parent=None, path=None, ivs=[]):
        #super(InputItem, self).__init__(parent)
        self.setIcon(0, QIcon(":/list.svg"))

class IVCurveItem(QTreeWidgetItem):
    def __init__(self, parent=None, path=None):
        #super(InputItem, self).__init__(parent)
        self.setIcon(0, QIcon(":/graph_dash.svg"))

class ExperimentalIVCurveItem(IVCurveItem):
    def __init__(self, parent=None, path=None):
        super(IVCurveItem, self).__init__(parent)
        self.setIcon(0, QIcon(":/iv_expt.svg"))

class TheoreticalIVCurveItem(IVCurveItem):
    def __init__(self, parent=None, path=None):
        super(IVCurveItem, self).__init__(parent)
        self.setIcon(0, QIcon(":/iv_theory.svg"))
        self.setFlags(self.flags())


if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    import sys
    app = QApplication(sys.argv)
    explorer = ProjectTreeWidget()
    explorer.show()
    app.exec_()
