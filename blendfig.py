import bpy
import numpy as np
from itertools import cycle


FIGURE_SIZE = 100
COLORS = [(1.,.24, .035, .75), (1., .05, .015, .75), (.4, .09,.26,.75), (.16,.07, .4, .75)]

color_cycle = cycle(COLORS)
default_color = (1.,.24, .035, .75)

class Figure:
    """ Figure object."""
    
    def __init__(self, size: tuple=(FIGURE_SIZE, FIGURE_SIZE)) -> None:
        
        self.traces = {}
        self.bounds = Bounds()
        
        self.trace_colors = {}
        

    def add_trace(self, trace):
        
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
        
        # update bounding box
        self.bounds.update(trace.bounds)
            
    def create(self):
        
        # creates the geometry for the figure
        for trace_type_list in self.traces.values():
            for trace in trace_type_list:
        
                trace.draw()

class Trace:
    
    """ Trace template """
    pass



class Surface(Trace):
    """ Surface trace """
    
    unnamed_surface_count = 0 # count how many unnamed surfaces have been created for consistent automatic naming.
    
    def __init__(self, x=None, y=None, z=None, name="Surface", color=None):
        
        # save input data
        self.x = np.array(x)
        self.y = np.array(y)
        self.z = np.array(z)
        
        # ensure z data, if no x or y replace with integer ranges
        if not self.z.any():
            raise ValueError("No z data given")
        if not self.x.any():
            self.x = np.arange(len(z))
        if not self.y.any():
            self.y = np.arange(len(z[0]))
        
        # save data bounds
        xmin, xmax = x.min(), x.max()
        ymin, ymax = y.min(), y.max()
        zmin, zmax = z.min(), z.max()
        
        self.bounds = Bounds([(xmin, xmax),(ymin, ymax),(zmin, zmax)])
        
        # name
        if name == "Surface":
            Surface.unnamed_surface_count += 1
            name += ' ' + str(Surface.unnamed_surface_count)
        self.name = name
        
        # set color to user input or cycle through 
        if color:
            self.color = color
        else:
            self.color = next(color_cycle)
        
        
    def draw(self):
        
        x_sub, y_sub = self.z.shape
        
        add_grid(x=self.bounds.x, y=self.bounds.y, subdivisions=(x_sub-1, y_sub-1))
        surface_from_grid(self.z)
        
        # rename object and mesh
        object = bpy.context.object
        object.name = self.name
        object.data.name = self.name
        
        # create and assign material
        material = bpy.data.materials.new(self.name)
        material.diffuse_color = self.color
        object.data.materials.append(material)
        print(f"Assigning material {material.name} color {self.color}\n Object: {object.name}\n {object.data.name}")
        
        
        

class Axes:
    
    def __init__(self, bounds):
        
        self.xbounds, self.ybounds, self.zbounds = bounds
        
    
class Bounds:
    """ Object for storing the bounds of geometry """
    
    def __init__(self, bounds=[(0,0),(0,0),(0,0)]):
        
        self.set_bounds(bounds)
    
    def set_bounds(self, bounds):
        
        # set bounds
        self.bounds = np.array(bounds)
        self.x = bounds[0]
        self.xmin, self.xmax = self.x
        self.y = bounds[1]
        self.ymin, self.ymax = self.y
        self.z = bounds[2]
        self.zmin, self.zmax = self.z
        
        # set center
        self.center = .5*(self.bounds[:,0] + self.bounds[:,1])
        
    def update(self, bounds):
        
        # recalculate the bounding box
        xmin = min(self.xmin, bounds.xmin)
        xmax = max(self.xmax, bounds.xmax)
        
        ymin = min(self.ymin, bounds.ymin)
        ymax = max(self.ymax, bounds.ymax)
        
        zmin = min(self.zmin, bounds.zmin)
        zmax = max(self.zmax, bounds.zmax)
        
        self.set_bounds(bounds=[(xmin,xmax),(ymin,ymax),(zmin,zmax)])
           
            
        
def delete_material(material=None):
    """ Delete materials. By default deletes all materials.
        Alternatively can give it instance or names of materials to be deleted.""" 
    
    project_materials = bpy.data.materials
    
    # if called with no arguments delete all
    if not material:
        for m in project_materials:
            project_materials.remove(m)
        return
        
    # single material instance
    if type(material) == bpy.types.Material:
        project_materials.remove(material)
        return
    
    # material name as string
    if type(material) == str:
        
        m = project_materials[material]
        project_materials.remove(m)
        return
    
    # iterable
    try:
        
        for m in material:
            
            # list of material instances
            if type(m) == bpy.types.Material:
                project_materials.remove(material)
            
            # list of names as strings
            elif type(m) == str:
                m = project_materials[m]
                project_materials.remove(m)
        
        return
        
    except Exception as e:
        
        print(e)        
            
                
                
        
        
        
    
    
        
        

def add_grid(x, y, subdivisions=100):
    """ Add a subdivided grid.
        - x, y are are tuples of the minimum and maximum in each direction.
        - if subdivisions is int or float this will be taken to be the number of subdivision in the x direction.
          The subdivisions in the y direction would be set automtically from the size of the grid to ensure square faces.
          Alterntively subdivisions can be a tuple (x_subdivisions, y_subdivisions).
    """
    
    # set dimensions
    xmin, xmax = x
    ymin, ymax = y
    location = (.5 * (xmin + xmax), .5 * (ymin + ymax), 0)
    size = xmax - xmin
    yscale = (ymax-ymin)/size
    
    # set subdivisions
    if type(subdivisions) is int or type(subdivisions) is float:
        x_sub = subdivisions
        y_sub = yscale*x_sub
    elif len(subdivisions) == 2:
        x_sub, y_sub = subdivisions
    else:
        raise ValueError("Acceptable inputs are int, float or an iterable of type (x_subdivisions, y_subdivisions)")
   
    
    # add and scale mesh    
    bpy.ops.mesh.primitive_grid_add(size=size, x_subdivisions=x_sub, y_subdivisions=y_sub, enter_editmode=False, align='WORLD', location=location)
    bpy.ops.transform.resize(value=(1, yscale, 1), mirror=False, use_proportional_edit=False)
    bpy.ops.object.transform_apply(scale=True)
    
def add_box(x, y, z):
    """ Add a box. x = (xmin, xmax) etc. """
    
    # set dimensions
    xmin, xmax = x
    ymin, ymax = y
    zmin, zmax = z
    location = (.5 * (xmin + xmax), .5 * (ymin + ymax), .5 * (zmin + zmax))
    size = xmax - xmin
    yscale = (ymax-ymin)/size
    zscale = (zmax-zmin)/size
    
    # add and scale mesh
    bpy.ops.mesh.primitive_cube_add(size=size, enter_editmode=False, align='WORLD', location=location)
    bpy.ops.transform.resize(value=(1, yscale, zscale), mirror=False, use_proportional_edit=False)
    bpy.ops.object.transform_apply(scale=True)

def surface_from_grid(z):
    """ Deform a flat grid (must be active) into a surface characterizad by z data. Data must match the vertex structure of the grid. """
    
    data = bpy.context.object.data
    
    xlen = len(z)
    
    for i, vert in enumerate(data.vertices):
        
        vert.co.z = z[i % xlen][int(i/xlen)]

def add_plane(size, location=(0, 0, 0), subdivide=100):
    """ Add a 2D plane and subdivid it """
    
    # parse input
    if type(size) is int or type(size) is float:
        
        if size <= 0:
            raise ValueError("Plane size must be posititive")
        
        x, y = size, size
        scale = 1
    
    elif len(size) == 2:
        x, y = size
        scale = y/x
        print(scale)
    
    else:
        raise ValueError("Acceptable inputs for size are int or float for a square plane or iterable of type (length, width)")
    
    # add and scale mesh
    bpy.ops.mesh.primitive_plane_add(size=x, enter_editmode=False, align='WORLD', location=location)
    bpy.ops.transform.resize(value=(1, scale, 1), mirror=False, use_proportional_edit=False)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


    # subdivide plane
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=subdivide-1)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # TODO: subdivide y axis proportionally possibly with loop cuts
    

def make_surface(f, size):
    
    data = bpy.context.object.data

    for vert in data.vertices:
        
        x, y, z = vert.co
        vert.co.z = f(x+size/2, y)
        
def f(x, y):
    
    return (.05*x**2 + np.sinh(y)**2)/np.cosh(y)**4


def make_curves():

    # go to edit edge select mode
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='EDGE')
    
    # select edge loop
    data = bpy.context.object.data
    edge = data.edges[500]
    edge.select = True
    bpy.ops.mesh.loop_multi_select(ring=False)

def main():

    size = 4
    resolution = 100

    add_plane(size, resolution)
    make_surface(f, size)
    add_plane(size, resolution)
    
    plane = bpy.data.objects['Plane']


    for i in range(10):
        make_x_curve(.2*i)
        bpy.context.view_layer.objects.active = plane
        make_y_curve(.2*i)
        if i != 0:
            bpy.context.view_layer.objects.active = plane
            make_x_curve(-.2*i)
            bpy.context.view_layer.objects.active = plane
            make_y_curve(-.2*i)
        bpy.context.view_layer.objects.active = plane

def make_x_curve(x, epsilon=1.e-5):
    
    bpy.ops.object.mode_set(mode='OBJECT')
    obj = bpy.context.active_object

    bpy.ops.object.mode_set(mode='EDIT') 
    bpy.context.tool_settings.mesh_select_mode = (False, True, False) # force edges
    bpy.ops.object.mode_set(mode='OBJECT')

    for edge in obj.data.edges:
        
        v1, v2 = edge.vertices
        v1 = obj.data.vertices[v1]
        v2 = obj.data.vertices[v2]
        
        # if the edeg is in y direction
        if abs(v1.co.x - v2.co.x) < epsilon and abs(v1.co.x - x) < epsilon:
            edge.select = True
        

    bpy.ops.object.mode_set(mode='EDIT')
    
    bpy.ops.mesh.duplicate()
    bpy.ops.mesh.separate(type='SELECTED')

    bpy.ops.object.mode_set(mode='OBJECT')
    
    plane, curve = bpy.context.selected_objects
    plane.select_set(False)
    bpy.context.view_layer.objects.active = curve
    curve.name = f"Curve.x={x:.1f}"
    bpy.ops.object.convert(target='CURVE')

def make_y_curve(y, epsilon=1.e-5):
    
    bpy.ops.object.mode_set(mode='OBJECT')
    obj = bpy.context.active_object

    bpy.ops.object.mode_set(mode='EDIT') 
    bpy.context.tool_settings.mesh_select_mode = (False, True, False) # force edges
    bpy.ops.object.mode_set(mode='OBJECT')

    for edge in obj.data.edges:
        
        v1, v2 = edge.vertices
        v1 = obj.data.vertices[v1]
        v2 = obj.data.vertices[v2]
        
        # if the edeg is in y direction
        if abs(v1.co.y - v2.co.y) < epsilon and abs(v1.co.y - y) < epsilon:
            edge.select = True
        

    bpy.ops.object.mode_set(mode='EDIT')
    
    bpy.ops.mesh.duplicate()
    bpy.ops.mesh.separate(type='SELECTED')

    bpy.ops.object.mode_set(mode='OBJECT')
    
    plane, curve = bpy.context.selected_objects
    plane.select_set(False)
    bpy.context.view_layer.objects.active = curve
    curve.name = f"Curve.y={y:.1f}"
    bpy.ops.object.convert(target='CURVE')





        
        
        
        
        
        


