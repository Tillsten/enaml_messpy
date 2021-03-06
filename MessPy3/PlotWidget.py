from atom.atom import observe
from atom.enum import Enum
import numpy as np
import atom.api as a
from enaml.core.api import Declarative, d_
from enaml.widgets.api import RawWidget

from pyqtgraph import PlotWidget, mkPen
from pyqtgraph.graphicsItems import PlotItem
from pyqtgraph.graphicsItems.PlotDataItem import PlotDataItem
import seaborn
seabborn_colors = seaborn.color_palette('bright')[1:]

class Line(Declarative):
    __slots__ = ('__weakrefs__')
    x = d_(a.Value([1,2,3]))
    y = d_(a.Value([1,2,3]))

    color = d_(a.Value('r'))
    width = d_(a.Float(1.))
    antialiased = d_(a.Bool(True))

    line : PlotDataItem = d_(a.Typed(PlotDataItem, args=([])))
    name : str = d_(a.Str())

    data_changed = a.Event()
    pen = a.Value()

    def _default_pen(self):
        return mkPen(color='r')

    def _default_line(self):
        return PlotDataItem(pen=self.pen)

    @observe('color', 'width')
    def make_pen(self, change):
        self.pen = mkPen(color=tuple(map(lambda x: 255*x, self.color)), width=self.width)
        self.line.setPen(self.pen)
        self.line.opts['antialias'] = self.antialiased

    #@a.observe('x', 'y')
    def set_data(self, x, y):
        self.x = np.array(x)
        self.y = np.array(y)
        self.line.setData(y=self.y, x=self.x)
        self.data_changed = True

class Plotter(RawWidget):
    __slots__ = ('__weakrefs__')
    widget = a.Value()


    hug_width = a.set_default('ignore')
    hug_height = a.set_default('ignore')

    has_new_data: bool = a.Bool()
    color_cycle: list = a.List()
    #minimum_size = (10000, 1000)

    grid = d_(Enum('y', 'x', 'both', 'none'))


    def _default_color_cycle(self):
        return seabborn_colors

    def names(self):
        return [l.name for l in self.children]

    def create_widget(self, parent):
        self.widget = PlotWidget(parent=parent)
        self.set_grid()
        for i, child in enumerate(self.children):
            if isinstance(child, Line):
                self.widget.addItem(child.line)
                child.color = self.color_cycle[i % len(self.color_cycle)]
                child.data_changed.bind(self.update_data)

        return self.widget

    def child_added(self, child):
        super().child_added(child)        
        if isinstance(child, Line) and self.is_initialized:
            self.widget.addItem(child.line)
            child.color = self.color_cycle[i % len(self.color_cycle)]
            child.data_changed.bind(self.update_data)
        return

    def child_removed(self, child):
        super().child_removed(child)
        if isinstance(child, Line): 
            self.widget.removeItem(child.line)
            child.data_changed.unbind(self.update_data)
        return 

    @observe('grid')
    def set_grid(self, changes=None):
        x_grid = self.grid in ('x', 'both')
        y_grid = self.grid in ('y', 'both')
        self.widget.plotItem.showGrid(x=x_grid, y=y_grid)

    def update_data(self, change):
        pass
