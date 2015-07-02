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
**matplotlibWidget.py** - defines 
'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib import rc

from copy import deepcopy

import dialogs

try:
    from cleed import iv as iv_
except ImportError:
    import sys
    import os
    module_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    module_path = os.path.join(module_path, 'cleed')
    sys.path.insert(0, module_path)
    import iv as iv_
    

class MplCanvas(FigureCanvas):
    '''class to provide a matplotlib PyQt canvas''' 
    def __init__(self):
        self.plt = plt
        self.fig = self.plt.figure()
        self.ax = self.fig.add_subplot(111, picker=True)
        self.ax.get_xaxis().set_picker(True)
        self.ax.get_yaxis().set_picker(True)
 
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, 
                    QtGui.QSizePolicy.Expanding,
                    QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

 
class MatplotlibWidget(QtGui.QWidget):
    '''class to provide a matplotlib PyQt widget'''
    PICKER = 5
    HIGHLIGHTER = dict(boxstyle='round,pad=0.25', 
                       alpha=0.5, 
                       facecolor='lightblue',
                       edgecolor='blue', 
                       linestyle='dashed',
                       linewidth=1.5,
                       hatch="/")
    
    def __init__(self, parent=None, title={'text':''}):
        QtGui.QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.canvas.fig.set_facecolor('white')
        self.vbl = QtGui.QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
        self._init_context_menu()
        self.canvas.setFocusPolicy( QtCore.Qt.ClickFocus )
        self.canvas.setFocus()
        self._plots = []
        self._active_obj = None
        self._active_dataset = None
        self._old_bbox = None

        # initialise selection box
        self._selection_box = mpl.patches.Rectangle((0, 0), 1, 1)
        for attr in self.HIGHLIGHTER: 
            try:
                eval("self._selection_box.set_{0}(self.HIGHLIGHTER['{0}'])"
                     "".format(attr))
            except:
                pass
        self._selection_box.set_visible(False)
        self.canvas.ax.add_patch(self._selection_box)
        
        # initialise title
        try:
            title_text = title.pop('text')
        except KeyError:
            title_text = ''
        try:
            title_bbox = title.pop('boxstyle')
        except:
            title_bbox = dict(alpha=0., fc='gray', boxstyle='square,pad=0.1')
            
        self.title(title_text, bbox=title_bbox, **title)
        
        # initialise connections
        self.canvas.mpl_connect('button_press_event', self.mousePressEvent)
        self.canvas.mpl_connect('button_release_event', self.mouseReleaseEvent)
        self.canvas.mpl_connect('motion_notify_event', self.mouseMoveEvent)
        self.canvas.mpl_connect('pick_event', self._on_pick)
        self.canvas.mpl_connect('key_press_event', self.keyPressEvent)
        self.canvas.mpl_connect('key_release_event', self.keyReleaseEvent)
        #self.canvas.mpl_connect('figure_enter_event', self._on_pick)
        #self.canvas.mpl_connect('figure_leave_event', self._on_pick)
        #self.canvas.mpl_connect('axes_enter_event', self._on_pick)
        #self.canvas.mpl_connect('axes_leave_event', self._on_pick)

    def _init_context_menu(self):
        import res_rc
        
        self._graph_menu = QtGui.QMenu()
        
        self._graph_menu.addAction(QtGui.QAction(QtGui.QIcon(":/arrow_right.svg"),
                                                "&Export graph", self,
                                                triggered=self._export,
                                                shortcut='Ctrl+Shift+E'))
        self._graph_menu.addAction(QtGui.QAction(QtGui.QIcon(":/save.svg"),
                                                "&Save data", self,
                                                triggered=self._save,
                                                shortcut='Ctrl+S'))                            
        
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._popupMenu)

    def _popupMenu(self, point):
        '''popup menu for explorer widget'''
        self._graph_menu.popup(self.mapToGlobal(point))

    def _export(self):
        return self._save()

    def _save(self):
        import os.path
        fd = QtGui.QFileDialog()
        filters = ['Images (*.png *.jpg)',
                   'Vector Graphics (*.ps *.svg)',
                   'Portable Document Format (*.pdf)', 
                   'All Files (*)']
        filename = str(fd.getSaveFileName(self, 
                                          caption='Save graph', 
                                          directory=os.path.expanduser('~/'),
                                          filter=';;'.join(filters),
                                          selectedFilter=filters[0])
                       )
        if filename:
            return self.save(filename)
        
    def save(self, filename, **kwargs):
        return self.canvas.plt.savefig(filename, **kwargs)

    def title(self, *args, **kwargs):
        if 'picker' not in kwargs:
            kwargs['picker'] = True
        return self.canvas.plt.title(*args, **kwargs)
        
    def plot(self, *args, **kwargs):
        self._plots.append(self.canvas.plt.plot(*args, **kwargs)[0])
    
    def legend(self, *args, **kwargs):
        if not self.has_legend():
            leg = self.canvas.plt.legend(*args, **kwargs)
        else:
            leg = self.canvas.ax.get_legend()
            
            defaults = dict(
                 loc=leg._get_loc(),
                 numpoints=leg.numpoints,
                 markerscale=leg.markerscale,
                 scatterpoints=leg.scatterpoints,
                 scatteryoffsets=None,
                 prop=leg.prop,
                 fontsize=leg._fontsize,

                 # spacing & pad defined as a fraction of the font-size
                 borderpad=leg.borderpad,
                 labelspacing=leg.labelspacing,
                 handlelength=leg.handlelength,
                 handleheight=leg.handleheight,
                 handletextpad=leg.handletextpad,
                 borderaxespad=leg.borderaxespad,
                 columnspacing=leg.columnspacing,
                 ncol=leg._ncol,
                 mode=leg._mode,
                 fancybox=None,
                 shadow=leg.shadow,
                 title=None,
                 framealpha=leg.get_frame().get_alpha(),
                 bbox_to_anchor=None, #leg.get_bbox_to_anchor(),
                 bbox_transform=None,
                 frameon=leg._drawFrame,
                 handler_map=None
             )

            if 'loc' not in kwargs:
                pos = leg._loc
                kwargs['loc'] = pos
            vis = leg.get_visible()
            
            excludes = ['picker', 'legendHandles', 'sketch', 'axes',
                        'figure', 'animated', 'legend_box']
            d = dict()
            ld = leg.__dict__
            for key in ld:
                if key.startswith('_'):
                    if key[1:] not in excludes:
                        d[key[1:]] = ld[key]
                elif key in excludes:
                    pass
                else:
                    d[key] = ld[key]
            
            d.update(kwargs)
            leg = self.canvas.plt.legend(*args, **defaults)
            leg.set_visible(vis)
    
        if leg.get_visible() is True:
            leg = leg.draggable(True)
            return leg.legend
        
        return leg
    
    @property
    def legend_labels(self):
        return self.canvas.ax.get_legend_handles_labels()[1]
    
    @property
    def plots(self):
        return self._plots
    
    @property
    def current_axis(self):
        return self.canvas.ax
    
    @property
    def current_plot(self):
        raise NotImplementedError
    
    def has_legend(self):
        return self.canvas.ax.legend_ is not None
    
    def modify_legend(self, **kwargs):
        l = self.canvas.ax.gca().legend_
    
        defaults = dict(
            loc = l._loc,
            numpoints = l.numpoints,
            markerscale = l.markerscale,
            scatterpoints = l.scatterpoints,
            scatteryoffsets = l._scatteryoffsets,
            prop = l.prop,
            # fontsize = None,
            borderpad = l.borderpad,
            labelspacing = l.labelspacing,
            handlelength = l.handlelength,
            handleheight = l.handleheight,
            handletextpad = l.handletextpad,
            borderaxespad = l.borderaxespad,
            columnspacing = l.columnspacing,
            ncol = l._ncol,
            mode = l._mode,
            fancybox = type(l.legendPatch.get_boxstyle())==mpl.patches.BoxStyle.Round,
            shadow = l.shadow,
            title = l.get_title().get_text() if l._legend_title_box.get_visible() else None,
            framealpha = l.get_frame().get_alpha(),
            bbox_to_anchor = l.get_bbox_to_anchor()._bbox,
            bbox_transform = l.get_bbox_to_anchor()._transform,
            frameon = l._drawFrame,
            handler_map = l._custom_handler_map,
        )
    
        if "fontsize" in kwargs and "prop" not in kwargs:
            defaults["prop"].set_size(kwargs["fontsize"])
    
        mpl.pyplot.legend(**dict(defaults.items() + kwargs.items()))
        
    @property
    def _legend_map(self):
        lined = dict()
        if self.has_legend() is False:
            return lined()
        
        legend = self.canvas.ax.legend_
        
        for legline, origline in zip(legend.get_lines(), self.plots):
            lined[legline] = origline
        
        return lined
    
    def _on_pick(self, event):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
        print(event)
        print(event.artist.__repr__())
        if event.mouseevent.dblclick is True and event.mouseevent.button is 1:
            if isinstance(event.artist, mpl.legend.Legend):
                dlg = dialogs.MplLegendDialog(self, legend=event.artist)
            elif isinstance(event.artist, mpl.lines.Line2D):
                dlg = dialogs.MplLineDialog(self, line=event.artist)
            elif isinstance(event.artist, mpl.text.Text):
                dlg = dialogs.MplLabelDialog(self, text=event.artist)
            elif isinstance(object, class_or_type_or_tuple):
                dlg = dialogs.MplAxisDialog(self, axis=event.artist)
            dlg.show()
        elif not event.mouseevent.dblclick and event.mouseevent.button == 1:
            if isinstance(event.artist, mpl.legend.Legend): 
                pass
            elif isinstance(event.artist, mpl.legend.DraggableLegend):
                event.artist.on_pick(event)
            elif isinstance(event.artist, mpl.lines.Line2D):
                self.active_dataset(event.artist)
            elif isinstance(event.artist, mpl.text.Text):
                pass
            self.active_object(event.artist)
        return True
    
    def _on_click(self, event):
        print('click:', event.artist)
    
    def keyPressEvent(self, event):
        print(event.key)
        obj = self.active_object()
        if event.key == 'escape':
            self.active_dataset()
            self.active_object(None, purge=True)
        elif event.key == 'ctrl+d':
            ads = self.active_dataset()
            try:
                index = self.plots.index(ads)
                self.canvas.ax.lines.remove(self.plots.pop(index))
                self.legend()
                self.active_dataset(None)
            except IndexError:
                pass
        elif event.key == 'ctrl+a':
            # add annotation
            an = self.canvas.ax.annotate('label', xy=(event.x, event.y),
                                         xycoords='figure pixels',
                                         horizontalalignment='center', 
                                         verticalalignment='center',
                                         picker=True,
                                         bbox=dict(boxstyle='round', fc='gray', alpha=0.5))
            an.draggable(True)
        elif event.key == 'ctrl+>':
            # enlarge active object
            if isinstance(obj, mpl.text.Text):
                obj.set_size(obj.get_size() + 2)
            elif isinstance(obj, mpl.axis.Axis):
                for lbl in obj.get_ticklabels():
                    lbl.set_size(lbl.get_size() + 2)  
        elif event.key == 'ctrl+<':
            # shrink active object
            if isinstance(obj, mpl.text.Text):
                obj.set_size(obj.get_size() - 2)
            elif isinstance(obj, mpl.axis.Axis):
                for lbl in obj.get_ticklabels():
                    lbl.set_size(lbl.get_size() - 2)
        elif event.key == 'ctrl+i':
            # toggle italics
            if isinstance(obj, mpl.text.Text):
                obj.set_style('italic' if obj.get_style() != 'italic' else 'normal')
            elif isinstance(obj, mpl.axis.Axis):
                for lbl in obj.get_ticklabels():
                    lbl.set_style('italic' if obj.get_style() != 'italic' else 'normal')
        elif event.key == 'ctrl+b':
            # toggle bold font face
            if isinstance(obj, mpl.text.Text):
                obj.set_weight('bold' if obj.get_weight() != 'bold' else 'normal')
            elif isinstance(obj, mpl.axis.Axis):
                for lbl in obj.get_ticklabels():
                    lbl.set_weight('bold' if obj.get_weight() != 'bold' else 'normal')
        elif event.key == 'ctrl+u':
            # toggle underscore
            pass
        elif event.key == 'ctrl+e':
            # set middle horizontal alignment
            if isinstance(obj, mpl.text.Text):
                obj.set_ha('center')
            elif isinstance(obj, mpl.axis.Axis):
                for lbl in obj.get_ticklabels():
                    lbl.set_ha('center')
        elif event.key == 'ctrl+l':
            # set left horizontal alignment
            if isinstance(obj, mpl.text.Text):
                obj.set_ha('left')
            elif isinstance(obj, mpl.axis.Axis):
                for lbl in obj.get_ticklabels():
                    lbl.set_ha('left')
        elif event.key == 'ctrl+r':
            # set right horizontal alignment
            if isinstance(obj, mpl.text.Text):
                obj.set_ha('right')
            elif isinstance(obj, mpl.axis.Axis):
                for lbl in obj.get_ticklabels():
                    lbl.set_ha('right')
        elif event.key == 'ctrl+h':
            # 'hide' object by setting alpha channel to 0
            pass 
        elif event.key == 'ctrl+p':
            # print whole canvas
            pass 
        elif event.key == 'ctrl+y':
            # undo
            raise NotImplementedError('Redo functionality is not yet implemented')
        elif event.key == 'ctrl+z':
            # redo
            raise NotImplementedError('Undo functionality is not yet implemented')
        elif event.key == 'down':
            inc = self.size().height() / 100.
            if isinstance(self.active_object(), mpl.text.Annotation):
                x, y = self._active_obj.get_position()
                self._active_obj.set_y(y - inc)
        elif event.key == 'up':
            inc = self.size().width() / 100.
            if isinstance(self.active_object(), mpl.text.Annotation):
                x, y = self._active_obj.get_position()
                self._active_obj.set_y(y + inc)
        elif event.key == 'right':
            inc = self.size().width() / 100.
            if isinstance(self.active_object(), mpl.text.Annotation):
                x, y = self.active_object().get_position()
                self.active_object().set_x(x + inc)
        elif event.key == 'left':
            inc = self.size().width() / 100.
            if isinstance(self.active_object(), mpl.text.Annotation):
                x, y = self._active_obj.get_position()
                self._active_obj.set_x(x - inc)
        elif event.key == 'ctrl+right':
            if isinstance(self.active_object(), mpl.text.Annotation):
                angle = self.active_object()._rotation or 0.
                self.active_object().set_rotation(angle + 360/100.)
        elif event.key == 'ctrl+left':
            inc = self.size().width() / 100.
            if isinstance(self.active_object(), mpl.text.Annotation):
                angle = self.active_object()._rotation or 0.
                self.active_object().set_rotation(angle - 360/100.)
        elif event.key == 'control':
            self._control = True
        # update drawing
        self.canvas.draw()
            
    def keyReleaseEvent(self, event):
        if event.key == 'control':
            self._control = False
    
    def mousePressEvent(self, event):
        if event.button == 1:
            self._mouse_down = True
            self._selection_box.set_x(event.x)
            self._selection_box.set_x(event.y)
            self._selection_box.set_width(1)
            self._selection_box.set_height(1)
            self._selection_box.set_visible(True)
            self.canvas.draw()
        
    def mouseReleaseEvent(self, event):
        if event.button == 1:
            self._mouse_down = False
            self._selection_box.set_visible(False)
            self.canvas.draw()
    
    def mouseMoveEvent(self, event):
        if event.button == 1 and self._mouse_down is True:
                x0, y0 = self._selection_box.get_xy()
                x, y = (event.x, event.y)
                self._selection_box.set_width(abs(x - x0))
                self._selection_box.set_height(abs(y - y0))
                if x < x0:
                    self._selection_box.set_x(x0)
                if y < y0:
                    self._selection_box.set_y(y0)
                self.canvas.draw()
                
    def remove_highlighting(self, obj):
        if obj is None:
            return
        if isinstance(obj, mpl.text.Text):
            if isinstance(self._old_bbox, mpl.patches.FancyBboxPatch):
                obj._bbox_patch = self._old_bbox
            else:
                try:
                    obj.set_bbox(self._old_bbox)
                except TypeError as e:
                    print(e.msg())
        elif isinstance(obj, mpl.axis.Axis):
            for i, lbl in enumerate(obj.get_ticklabels()):
                if isinstance(self._old_bbox, mpl.patches.FancyBboxPatch):
                    lbl._bbox_patch = self._old_bbox[i]
                else:
                    try:
                        lbl.set_bbox(self._old_bbox[i])
                    except TypeError as e:
                        print(e.msg())
        elif isinstance(obj, mpl.legend.Legend):
            for key in self._old_bbox:
                eval("obj.legendPatch.set_{0}(self._old_bbox['{0}'])".format(key))
            
    def active_object(self, obj=None, purge=False):
        if purge:
            self.remove_highlighting(self._active_obj)
            self._active_obj = None
            obj = None
        
        if obj is not None:
            old_obj = self._active_obj 
            self._active_obj = obj
            self.remove_highlighting(old_obj)
        
        # apply highlighting for active object
        if isinstance(obj, mpl.lines.Line2D):
            self.active_dataset(obj)
        elif isinstance(obj, mpl.axis.Axis):
            self._old_bbox = [lbl.get_bbox_patch() or lbl._bbox for lbl 
                              in obj.get_ticklabels()]
            for lbl in obj.get_ticklabels():
                lbl.set_bbox(self.HIGHLIGHTER)
        elif isinstance(obj, mpl.text.Text):
            self._old_bbox = obj.get_bbox_patch() or obj._bbox
            obj.set_bbox(self.HIGHLIGHTER)
        elif isinstance(obj, mpl.legend.Legend):
            self._old_bbox = {}
            for key in self.HIGHLIGHTER:
                self._old_bbox[key] = eval("obj.legendPatch.get_{}()".format(key))
                eval("obj.legendPatch.set_{0}(self.HIGHLIGHTER['{0}'])".format(key))
        
        # update graph
        self.canvas.draw()
            
        return self._active_obj
        
    def active_dataset(self, dataset=None, alpha_vis=0.4):

        if dataset is not None and isinstance(dataset, mpl.lines.Line2D):
            self._active_dataset = dataset
        elif not hasattr(self, "_active_dataset"):
            self._active_dataset = None
        
        # toggle visability of datasets
        legend = self.canvas.ax.legend_
        if dataset is None:
            for legline, origline in zip(legend.get_lines(), self.plots):
                origline.set_alpha(1.)
                legline.set_alpha(1.)
        else:
            for legline, origline in zip(legend.get_lines(), self.plots):
                if origline == dataset:
                    alpha = 1.
                else:
                    alpha = alpha_vis
                origline.set_alpha(alpha)
                legline.set_alpha(alpha)
        self.canvas.draw()
        
        return self._active_dataset
    

class IVCurveWidget(MatplotlibWidget):
    EXPORTS = {'graph': 'png', 
               'vector': 'pdf', 
               'data': 'iv',
               None: None}
    
    def __init__(self, parent=None, iv=None, *args, **kwargs):
        # initialise base class
        MatplotlibWidget.__init__(self, *args, **kwargs)
        
        # setup canvas for IV specific plots
        self.canvas.plt.xlabel('Energy (eV)', 
                               fontsize='large', 
                               picker=True)
        self.canvas.plt.ylabel('Intensity (arb. units)', 
                               fontsize='large', 
                               picker=True)
        self.ivs = []
        self.plot_iv(iv)
        
    def _init_context_menu(self):
        MatplotlibWidget._init_context_menu(self)
        self._graph_menu.addSeparator()
        self._graph_menu.addAction(QtGui.QAction(QtGui.QIcon(":/graph_smooth.svg"),
                                                    "S&mooth...", self,
                                                    triggered=self._smooth))
    
    def _export(self):
        import os.path
        files = []
        fd = QtGui.QFileDialog()
        filters = ['IV data (*.iv *.xy *.cur *.fsm)', 
                   'All Files (*)']
        filename = str(fd.getSaveFileName(self, 
                                          caption='Save IV data', 
                                          directory=os.path.expanduser('~/'),
                                          filter=';;'.join(filters),
                                          selectedFilter=filters[0]))
        if filename:
            plots = self.plots
            labels = self.legend_labels
            if len(labels) < len(plots):
                labels += range(len(labels), len(plots))
            for i, curve in enumerate(plots):
                basename, ext = os.path.splitext(filename)
                fname = basename + str(labels[i]) + ext
                with open(fname, 'w') as f:
                    f.write('# {}\n'.format(labels[-1]))
                    x, y = plots[i][0].get_data()
                    for j in range(len(x)):
                        f.write('{:20.6f} {:20.6f}\n'.format(x[j], y[j]))
                    # append on success
                    files.append(fname)
        return files
                    
    def _smooth(self):
        from dialogs import SmoothDialog
        a = SmoothDialog(self)
        if a.exec_():
            i = a.selected_dataset()
            self.ivs.append(self.ivs[i].smooth())
            label_text = self.plots[i]._label + '_smoothed' or 'smoothed'
            self.plot(self.ivs[i].x, self.ivs[i+1].y, 'b--', 
                      label=label_text, 
                      picker=self.PICKER)
            self.legend()
            self.canvas.draw()
        
        
    def save(self, filename='', export='graph', plots=[]):
        filename = filename or '{}.{}'.format(self.name, self.EXPORTS[export])
        kwargs = {'format': self.EXPORTS[export]} if export is not None else {} 
        if export == 'data':
            return self._export()
        else: 
            return self.canvas.plt.savefig(filename, **kwargs)
        
    def plot_iv(self, iv, *args, **kwargs):
        title  = ''
        try:
            if isinstance(iv, iv_.IVCurvePair):
                title = os.path.basename(iv.experiment.path)
                title = str(iv.index) if iv.index else title
                self.legend(frameon=False, fontsize='medium', picker=True)
                self.ivs.append(iv)
                MatplotlibWidget.plot(self, 
                                      iv.experiment.x, 
                                      iv.experiment.y, 
                                      'k-', 
                                      label='Experiment',
                                      picker=self.PICKER)
                MatplotlibWidget.plot(self, 
                                      iv.theory.x, 
                                      iv.theory.y, 
                                      'r--', label='Theory',
                                      picker=self.PICKER)
                self.title(title, fontsize='large', picker=True)
            elif isinstance(iv, iv_.IVCurveGroup):
                self = IVGroupWidget(*args, **kwargs) 
            elif isinstance(iv, iv_.IVCurve):
                title = iv.path or ''
                self.ivs.append(iv)
                MatplotlibWidget.plot(self, iv.x, iv.y, 'k-', 
                                      label='IV_'+str(len(self.legend_labels)),
                                      picker=self.PICKER)
                self.title(title, fontsize=24, picker=True)
                self.legend()
                #self.legend.set_visible(False)
            elif iv is None:
                pass
            else:
                raise TypeError('iv must be an IVCurve or IVCurvePair')
        except AttributeError:
            raise
    
    
class IVGroupWidget(MatplotlibWidget):
    def __init__(self):
        raise NotImplementedError


class MatplotlibWidgetDemo(QtGui.QMainWindow):
    '''demo showing matplotlibWidget class'''
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self)
        
        
        import random
        import numpy as np

        x = np.arange(0, 5, 0.1);
        y = np.sin([ix + np.random.normal(ix)*0.15 for ix in x])
        
        iv = iv_.IVCurve(data=[x,y], path=str('test'))

        widget = IVCurveWidget(iv=iv)
        self.setCentralWidget(widget)


if __name__ == '__main__':
    import sys
    
    app = QtGui.QApplication(sys.argv)

    main = MatplotlibWidgetDemo()
    main.show()

    sys.exit(app.exec_())
