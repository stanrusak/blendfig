from .traces.trace import Trace
from .traces.surface import Surface
from .traces.scatter import Scatter
from .traces.bar import Bar
from .bounds.bounds import Bounds
from .axes.axes import Axes
from .materials.colors import COLORS, cycle

FIGURE_SIZE = 100
__version__ = '0.1.0'

class Figure:
    """ Figure object."""
    
    def __init__(self, size: tuple=(FIGURE_SIZE, FIGURE_SIZE)) -> None:
        
        self.traces = {}
        self.bounds = Bounds()
        self.ax = Axes(self.bounds.bounds)
        
        self.trace_colors = {}        

    def add_trace(self, trace: Trace) -> None:
        
        # add trace to the trace dictionary
        if (trace_type:=type(trace)) in self.traces:
            
            self.traces[trace_type].append(trace)
        
        else:
            
            self.traces[trace_type] = [trace]
        
        # if no color info in the trace, cycle through figure's colors
        if trace_type not in self.trace_colors:
            self.trace_colors[trace_type] = cycle(COLORS)
        if not trace.color:
            color = next(self.colors[trace_type])
            trace.color = color
            print(color)
        
        # update bounding box and axes
        self.bounds.update(trace.bounds)
        self.ax.update(trace.bounds.bounds)
            
    def create(self):
        
        # creates the geometry for the figure
        for trace_type_list in self.traces.values():
            for trace in trace_type_list:
        
                trace.draw()
        
        # draw axes
        self.ax = Axes(self.bounds.bounds)
        self.ax.draw()