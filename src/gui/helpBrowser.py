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
** helpBrowser.py ** - PyQt module for viewing CLEED HTML help files 
(generated using Sphinx or Doxygen). 
'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

from PyQt4 import QtCore, QtGui
import res_rc

import os

class DownloadProgressDialog(QtGui.QProgressDialog):
    def __init__(self, parent=None):
        super(QtGui.QProgressDialog, self).__init__(parent)
        
    def download(self, url, msg=None):
        import urllib2
        import tempfile
        file_name = os.path.join(tempfile.gettempdir(), url.split('/')[-1])
        
        if os.path.exists(file_name):
            return file_name
        
        u = urllib2.urlopen(url)
        f = open(file_name, 'wb')
        meta = u.info()
        msg = msg or url.split('/')[-1]
        file_size = int(meta.getheaders("Content-Length")[0])
        self.setWindowTitle("Downloading: '{}'".format(msg))
        print("Downloading: %s Bytes: %s" % (file_name, file_size))
        
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
        
            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, 
                                           file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            self.setValue(file_size_dl * 100. / file_size)
        
        f.close()
        return file_name
        

class HelpBrowser(QtGui.QTextBrowser):
    def __init__(self, parent=None):
        super(QtGui.QTextBrowser, self).__init__(parent)
        self.setWindowTitle('CLEED Help')
        self.setWindowIcon(QtGui.QIcon(':/question.svg'))
        #self.setSource(QtCore.QUrl(self.findHomeUrl()))
        self.setSearchPaths([":/help/html/"])
        src = QtCore.QUrl("index.html")
        self.setSource(src)
        self.resize(500, 400)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setAttribute(QtCore.Qt.WA_GroupLeader)
        self.home()
        
    def findHomeUrl(self):
        help_path = os.path.join('_build', 'html', 'index.html')
        root_path = os.path.dirname(os.path.dirname(__file__))
        home = os.path.join(root_path, 'doc', help_path)
        if os.path.exists(home):
            return home
        else:
            dlg = DownloadProgressDialog(self)
            url = 'https://bitbucket.org/cleed/documentation/get/b4e562ca6c4a.zip'
            dlg.setValue(0)
            dlg.exec_()
            filename = dlg.download(url, msg='help files')
            
            from zipfile import ZipFile, is_zipfile
            
            if is_zipfile(filename):
                zip = ZipFile(filename, 'r')
                path = os.path.join(os.path.dirname(filename), 
                                    os.path.basename(os.path.splitext(filename)[0]))
                if not os.path.exists(path):
                    os.makedirs(path)
                zip.extractall(path)
                
                return os.path.join(path, os.listdir(path)[0], help_path)
            
            
            
            
        

if __name__ == '__main__':
    import sys
    
    app = QtGui.QApplication(sys.argv)

    main = HelpBrowser()
    main.show()

    sys.exit(app.exec_())
    
