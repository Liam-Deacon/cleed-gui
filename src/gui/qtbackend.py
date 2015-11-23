import sys
import os

default_variant = 'PySide'

env_api = os.environ.get('QT_API', 'pyqt')
if '--pyside' in sys.argv:
    variant = 'PySide'
elif '--pyqt4' in sys.argv:
    variant = 'PyQt4'
elif env_api == 'pyside':
    variant = 'PySide'
elif env_api == 'pyqt':
    variant = 'PyQt4'
else:
    variant = default_variant

if variant == 'PySide':
    from PySide import QtCore, QtGui, QtNetwork, QtSvg
    sys.modules[__name__ + '.QtCore'] = QtCore
    sys.modules[__name__ + '.QtGui'] = QtGui
    sys.modules[__name__ + '.QtNetwork'] = QtNetwork
    sys.modules[__name__ + '.QtSvg'] = QtSvg
    try:
        from PySide import QtOpenGL
        sys.modules[__name__ + '.QtOpenGL'] = QtOpenGL
    except ImportError:
        pass
    try:
        from PySide import QtWebKit
        sys.modules[__name__ + '.QtWebKit'] = QtWebKit
    except ImportError:
        pass
    QtCore.QT_VERSION_STR = QtCore.__version__
    QtCore.QT_VERSION = tuple(int(c) for c in QtCore.__version__.split('.'))    
    for attr in ['pyqtSignal', 'pyqtSlot', 'pyqtProperty']:
        if not hasattr(QtCore, attr):
            eval("QtCore.{} = QtCore.{}".format(attr[4:], attr))
    # This will be passed on to new versions of matplotlib
    os.environ['QT_API'] = 'pyside'
    def QtLoadUI(uifile, obj=None):
        from PySide import QtUiTools
        loader = QtUiTools.QUiLoader()
        uif = QtCore.QFile(uifile)
        uif.open(QtCore.QFile.ReadOnly)
        result = loader.load(uif, obj)
        uif.close()
        return result

elif variant == 'PyQt4':
    import sip
    api2_classes = ['QData', 'QDateTime', 'QString', 'QTextStream',
                    'QTime', 'QUrl', 'QVariant',]
    for cl in api2_classes:
        sip.setapi(cl, 2)
    from PyQt4 import QtCore, QtGui, QtNetwork, QtSvg
    sys.modules[__name__ + '.QtCore'] = QtCore
    sys.modules[__name__ + '.QtGui'] = QtGui
    sys.modules[__name__ + '.QtNetwork'] = QtNetwork
    sys.modules[__name__ + '.QtSvg'] = QtSvg
    try:
        from PyQt4 import QtOpenGL
        sys.modules[__name__ + '.QtOpenGL'] = QtOpenGL
    except ImportError:
        pass
    try:
        from PyQt4 import QtWebKit
        sys.modules[__name__ + '.QtWebKit'] = QtWebKit
    except ImportError:
        pass
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot
    QtCore.Property = QtCore.pyqtProperty
    QtCore.QString = str
    os.environ['QT_API'] = 'pyqt'
    def QtLoadUI(uifile, obj=None):
        from PyQt4 import uic
        return uic.loadUi(uifile, obj)
else:
    raise ImportError("Python Variant not specified")

def get_qt_binding_name():
    return variant

__all__ = [QtGui, QtCore, QtLoadUI, get_qt_binding_name]
