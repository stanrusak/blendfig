from ..geometry.geometry import add_box
from ..bounds.bounds import Bounds
import numpy as np
import bpy

class Axes:
    """ Object for storing information about and drawing the axes. """
    
    def __init__(self, bounds, ticks='auto'):
        
        self.bounds = bounds

        self.ticks = ticks
        self.num_ticks = (10,10,6)
    
    def update(self, bounds):
        
        self.bounds = bounds
        
    def draw(self):
        
        if hasattr(self.bounds, 'rescaled'):
            add_box(*self.bounds.rescaled.bounds)
        else:
            add_box(*self.bounds.bounds)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.object.data.vertices[-1].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # draw ticks
        if self.ticks:

            for axis in range(3):
                
                # if no input calculate ticks auomatically
                physical_bounds = self.bounds.bounds if not hasattr(self.bounds, 'rescaled') else self.bounds.rescaled.bounds
                if self.ticks == 'auto':
                    ticks = automatic_ticks(*self.bounds.bounds[axis], num_ticks=self.num_ticks[axis])
                    tick_locations = automatic_ticks(*physical_bounds[axis], num_ticks=self.num_ticks[axis])
                # otherwise take from input    
                else:
                    ticks = self.ticks[axis]
                
                add_ticks(ticks, tick_locations, axis, bounds=physical_bounds)

def nice_number(value, round=False):
    
    exponent = np.floor(np.log10(value))
    fraction = value / 10 ** exponent

    if round:
        if fraction < 1.5:
            nice_fraction = 1.
        elif fraction < 3.:
            nice_fraction = 2.
        elif fraction < 7.:
            nice_fraction = 5.
        else:
            nice_fraction = 10.
    else:
        if fraction <= 1:
            nice_fraction = 1.
        elif fraction <= 2:
            nice_fraction = 2.
        elif fraction <= 5:
            nice_fraction = 5.
        else:
            nice_fraction = 10.

    return nice_fraction * 10 ** exponent

def automatic_ticks(min_val, max_val, num_ticks=10):

    axis_width = max_val - min_val
    if axis_width == 0:
        nice_tick = 0
    else:
        nice_range = nice_number(axis_width)
        nice_tick = nice_number(nice_range / (num_ticks - 1), round=True)
        axis_start = np.floor(min_val / nice_tick) * nice_tick
        axis_end = np.ceil(max_val / nice_tick) * nice_tick

    ticks = np.arange(axis_start, axis_end + nice_tick, nice_tick)
    
    # round to get rid of floating point imprecision
    if np.log10(nice_tick) > -14:
        ticks = np.round(ticks, 15) + 0.
    
    return ticks
    
def add_ticks(ticks, tick_locations, axis, bounds, size = .5, offset = .2):
    
    xmin, xmax = bounds[0]
    ymin, ymax = bounds[1]
    zmin, zmax = bounds[2]
    
    if axis == 0:
        rotation = (0, 0 ,np.pi/2)
        initial_location = [0, ymax + offset, zmin]
    elif axis == 1:
        rotation = (0, 0, np.pi)
        initial_location = [xmax + offset , 0, zmin]
    elif axis == 2:
        rotation = (np.pi/2, 0, 3*np.pi/4)
        initial_location = [xmax + offset/3, ymin - offset/3, 0]
        
    for tick, tick_location in zip(ticks, tick_locations):
        
        location = initial_location
        location[axis] = tick_location
        
        bpy.ops.object.text_add(location=location, rotation=rotation, scale=(1, 1, 1))
        text_data = bpy.context.object.data
        text_data.body = f"{tick:.01f}"
        text_data.size = size
        if axis:
            text_data.align_x = 'RIGHT'
        text_data.align_y = 'CENTER'