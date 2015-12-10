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
'''

'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

from qtbackend import QtCore, QtGui

import os.path
try:
    import res_rc
except:
    pass

try:
    import core
except ImportError:
    import sys
    import os
    module_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    module_path = os.path.join(module_path, 'core')
    sys.path.insert(0, module_path)
    import core

class ProjectTreeWidget(QtGui.QTreeWidget):
    def __init__(self, parent=None):
        super(ProjectTreeWidget, self).__init__(parent)
        
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
        self.newProjectAction.setToolTip(
                                    "Opens project location in file explorer")
        
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
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.explorerPopupMenu)
        
        #recent projects
        self.recent_projects = []
    
    def expandChildren(self, index):
        ''' Recursely expands all children for the given index node'''
        if not index.isValid():
            return

        childCount = index.model().rowCount(index)
        for i in range(childCount):
            child = index.child(i, 0)
            # Recursively call the function for each child node.
            expandChildren(child)

        if not view.expanded(index):
            view.expand(index)
    
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
                print('another item: %s' % item)
        else:
            # provide default menu
            self.explorerDefaultMenu.popup(
                        self.viewport().mapToGlobal(point))
    
    def currentProject(self):
        '''returns the currently selected project'''
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
        folder = QtGui.QFileDialog.getExistingDirectory(parent=self, 
                            caption="Select Project Base Directory",
                            directory=projectDir, 
                            options=QtGui.QFileDialog.ShowDirsOnly | 
                                    QtGui.QFileDialog.DontResolveSymlinks)    
        if folder:
            # do stuff
            items = [self.parent().topLevelItem(i).Path for i 
                     in range(self.parent().topLevelItemCount())]
            if folder not in items:
                proj = ProjectItem(self.ui.parent(), path=folder)
            else:
                pass
                self.parent().setCurrentIndex(0, items.index(folder, ))
    
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
                                                  QtGui.QLineEdit.Normal,
                                                  old_name)
        if ok and new_name is not old_name:
            item = project['item']
            item.setText(self.currentColumn(), new_name) 
        
        
    def refresh(self):
        raise NotImplementedError('todo')
    
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


class BaseItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent=None):
        super(BaseItem, self).__init__(parent)
    
    @classmethod
    def getChildren(cls, parent, recursive=True):
        ''' Get either immediate or all children of parent node ''' 
        children = []
        for i in range(parent.childCount()):
            child = parent.child(i)
            children += [child]
            if recursive:
                children += BaseItem.getChildren(child, recursive)
        return children

class ProjectItem(BaseItem):
    projects = []
    
    '''class for project items'''
    def __init__(self, parent=None, path=None):
        super(ProjectItem, self).__init__(parent)
        self.setProjectPath(path)
        self.setIcon(0, QtGui.QIcon(":/folder_fill.svg"))
        self.name = "New_Project{}".format(len(self.projects))
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
        #self.setProjectPath(path)
        
        self.models = []
        
        #add children
        self._init_children()
        
        ProjectItem.projects.append(self)
    
    def _init_children(self):
        model = ModelItem(self)
        self.models.append(model)
        self.addChild(model)
        
    def __del__(self):
        try:
            ProjectItem.projects.remove(self)
        except:
            pass
    
    @classmethod
    def load(cls, directory):
        pass
    
    @property
    def project_path(self):
        return self._path
    
    @project_path.setter
    def project_path(self, path):
        self._path = path
    
    def setProjectPath(self, path):
        path = path 
        self.setText(0, 'Project{}'.format(len(ProjectItem.projects)))
        self.setToolTip(0, path)
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name
    
        
class ModelItem(BaseItem):
    '''class for project items'''
    def __init__(self, parent=None, path=None):
        super(ModelItem, self).__init__(parent)
        self.setIcon(0, QtGui.QIcon(":/blocks.svg"))
        self.setText(0, "New_Model")
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
        #self.setModelName(path)
        
        # init items
        self.surface = InputItem()
        self.bulk = BulkItem()
        self.iv_groups = IVGroupItem()
        
        self.addChild(self.surface)
        self.addChild(self.bulk)
        
        self.addChild(self.iv_groups)
    
    def setModelName(self, path):
        self.Path = path
        self.Name = QFileInfo(path).baseName()
        self.setText(0, self.Name)
        self.setToolTip(0, path)
        
    def addGroup(self, group=None):
        if group is None:
            # create default group
            group = IVGroupItem()
        
        if isinstance(group, IVGroupItem):
            self.addChild(group)
        
            

class InputItem(BaseItem):
    '''class for project items'''
    def __init__(self, parent=None, input=None):
        super(InputItem, self).__init__(parent)
        self.setIcon(0, QtGui.QIcon(":/minus.svg"))
        self.setText(0, 'Surface_Model')
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
        
        self.model = None
      
class BulkItem(BaseItem):
    '''class for project items'''
    def __init__(self, parent=None, bulk=None):
        super(BulkItem, self).__init__(parent)
        self.setIcon(0, QtGui.QIcon(":/layers.svg"))
        self.setText(0, "Bulk_Model")
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
        
        self.model = None
        
        
class SearchItem(BaseItem):
    '''class for LEED-IV control items'''
    def __init__(self, parent=None, path=None):
        #super(InputItem, self).__init__(parent)
        self.setIcon(0, QtGui.QIcon(":/cog.svg"))
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)


class SettingsItem(BaseItem):
    '''class for local settings'''
    def __init__(self, parent=None, path=None):
        #super(InputItem, self).__init__(parent)
        self.setIcon(0, QtGui.QIcon(":/wrench.svg"))
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
        
        
class IVGroupItem(BaseItem):
    '''class for handling LEED-IV curves'''
    def __init__(self, parent=None, path=None, ivs=[]):
        super(IVGroupItem, self).__init__(parent)
        self.setIcon(0, QtGui.QIcon(":/list.svg"))
        self.setText(0, 'IV_Group')
        
        # initialise actions
        self.iv_pairs = [IVInfoItem()]
        
        for iv in self.iv_pairs:
            self.addChild(iv)
        
        # initialise other aspects
        self.theta = QtGui.QTreeWidgetItem()
        self.theta.setText(0, 'Theta')
        self.theta.setIcon(0, QtGui.QIcon(':/theta.svg'))
        
        self.phi = QtGui.QTreeWidgetItem()
        self.phi.setText(0, 'Phi')
        self.phi.setIcon(0, QtGui.QIcon(':/phi.svg'))
        
        self.enabled = QtGui.QTreeWidgetItem()
        self.enabled.setText(0, 'Enabled')
        self.enabled.setIcon(0, QtGui.QIcon(':/check.svg'))
        
        self.rfactor = QtGui.QTreeWidgetItem()
        self.rfactor.setText(0, 'Rfactor')
        self.rfactor.setIcon(0, QtGui.QIcon(':/rf.svg'))
        
        self.addChildren([self.theta, self.phi, self.enabled, self.rfactor])
        
    @classmethod
    def readControlFile(cls, ctr):
        pass
    
    def _createActions(self):
        self.generateControlAction = QtGui.QAction(
                                    QtGui.QIcon(":/document_edit_24x32.png"),
                                    "&Edit ctr file...", 
                                    self,
                                    triggered=self.viewControl,
                                    shortcut='Ctrl+E')
        self.generateControlAction.setToolTip("Edit LEED control file...")

    def viewControl(self):
        pass

class IVInfoItem(BaseItem):
    def __init__(self, parent=None, iv_pair=None):
        super(IVInfoItem, self).__init__(parent)
        self.setIcon(0, QtGui.QIcon(":/index.svg"))
        self.setText(0, '(h, k)')
        
        self.expt = ExperimentalIVCurveItem()
        self.theory = TheoreticalIVCurveItem()
        
        self.id = QtGui.QTreeWidgetItem()
        self.id.setText(0, 'ID')
        self.id.setIcon(0, QtGui.QIcon(":/id.svg"))
        
        self.weight = QtGui.QTreeWidgetItem()
        self.weight.setText(0, 'Weight')
        self.weight.setIcon(0, QtGui.QIcon(":/eject.svg"))
        
        self.rfactor = QtGui.QTreeWidgetItem()
        self.rfactor.setText(0, 'Rfactor')
        self.rfactor.setIcon(0, QtGui.QIcon(':/rf.svg'))
        
        self.addChildren([self.expt, self.theory, self.id, 
                          self.weight, self.rfactor])
        
        try:
            if isinstance(iv_pair, IVCurvePair):
                self.load(iv_pair)
        except:
            pass
            
        def load(self, iv_pair):
            pass


class IVCurveItem(BaseItem):
    def __init__(self, parent=None, path=None):
        super(IVCurveItem, self).__init__(parent)
        self.setIcon(0, QtGui.QIcon(":/graph_dash.svg"))
        self.setText(0, "IV curve")


class ExperimentalIVCurveItem(IVCurveItem):
    def __init__(self, parent=None, path=None):
        super(ExperimentalIVCurveItem, self).__init__(parent)
        self.setIcon(0, QtGui.QIcon(":/iv_expt.svg"))
        self.setText(0, "Experimental IV")


class TheoreticalIVCurveItem(IVCurveItem):
    def __init__(self, parent=None, path=None):
        super(TheoreticalIVCurveItem, self).__init__(parent)
        self.setIcon(0, QtGui.QIcon(":/iv_theory.svg"))
        self.setText(0, "Theoretical IV")
        self.setFlags(self.flags())


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    explorer = ProjectTreeWidget()
    
    project = ProjectItem()
    #pro2 = ProjectItem()
    explorer.addTopLevelItem(project)
    for child in project.getChildren(project):
        child.setExpanded(True)
    #explorer.addTopLevelItem(pro2)
    
    explorer.show()
    app.exec_()
