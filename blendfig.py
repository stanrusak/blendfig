import bpy, os
import numpy as np
from numpy import pi
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
        self.ax = Axes(self.bounds.bounds)
        
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

class Trace:
    
    """ Trace template """
    pass

class Scatter(Trace):
    """ Object for scatter and line plots """
    
    def __init__(self, x=None, y=None, z=None, name="Scatter"):
        
        self.name = name
        self.active_axes = [] # non-zero axes 
        
        self.x, self.y, self.z, self.point_num = 0, 0, 0, 0
        if not x is None:
            self.x = x
            self.active_axes.append("x")
            self.point_num = len(self.x)
        if not y is None:
            self.y = y
            self.active_axes.append("y")
            
            if self.point_num and self.point_num != len(self.y):
                raise ValueError("Length of x and y do not match")
            else:
                self.point_num = len(self.y)                
        if not z is None:
            self.z = z
            
            if self.active_axes:
                if len(z) != self.point_num:
                    raise ValueError(f"Length of z and {self.active_axes[0]} do not match")             
            self.active_axes.append("z")
        
    
    def draw(self):
        
        mesh = bpy.data.meshes.new(self.name)
        mesh.vertices.add(self.point_num)
        mesh.edges.add(self.point_num-1)
        
        if not (type(self.x) is int):
            
            # convert to array in case is dataframe
            x = np.array(self.x)
            
            # if data is not numbers replace by range
            if x.dtype != 'float' and x.dtype != 'int':
                x = np.arange(0, x.shape[0])
        else:
            x = 0 * np.ones(self.point_num)
            
        if not (type(self.y) is int):
            
            # convert to array in case is dataframe
            y = np.array(self.y)
            
            # if data is not numbers replace by range
            if y.dtype != 'float' and y.dtype != 'int':
                y = np.arange(0, y.shape[0])
        else:
            y = 0 * np.ones(self.point_num)
            
        if not (type(self.z) is int):
            
            # convert to array in case is dataframe
            z = np.array(self.z)
            
            # if data is not numbers replace by range
            if z.dtype != 'float' and z.dtype != 'int':
                z = np.arange(0, z.shape[0])
        else:
            z = 0 * np.ones(self.point_num)
        
        
        
        for i in range(self.point_num):
            
            mesh.vertices[i].co = x[i], y[i], z[i]
            
            if i < self.point_num-1:
                mesh.edges[i].vertices = (i,i+1)
                
        object = bpy.data.objects.new(self.name, mesh)
        #c = bpy.data.collections.get('Collection')
        bpy.context.collection.objects.link(object)
        bpy.context.view_layer.objects.active = object
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()
        
        self.mesh_object = object
        
        return object
    
    def draw_zlabels(self,labels=None):
        """ Add floating labels indicating z-values. The text objects are generated
            from data and then positioned using geometry nodes for greater customizability. """
        
        if not labels:
            labels = self.z
        
        # make a collection of labels
        collection = add_text(labels, name=self.name + " zlabels")
        
        # add a text obect to put geometry nodes on
        labels_object = add_text(self.name + " ZLabels", name=self.name + " ZLabels")
        
        
        if 'ZLabels' not in bpy.data.node_groups:
            append_nodetree('ZLabels')
          
        geonodes = labels_object.modifiers.new('ZLabels' + ' ' + self.name, type='NODES')
        geonodes.node_group = bpy.data.node_groups['ZLabels']
        geonodes.node_group.nodes['Object Info'].inputs[0].default_value = self.mesh_object
        geonodes.node_group.nodes['Collection Info'].inputs[0].default_value = collection
        
    def draw_xlabels(self,labels=None):
        """ Add labels indicating x-values. The text objects are generated
            from data and then positioned using geometry nodes for greater customizability.
        """
            
        if not labels:
            labels = self.x
        
        # make a collection of labels
        collection = add_text(labels, name=self.name + " xlabels", align_x='RIGHT')
        collection.hide_viewport = True
        collection.hide_render = True
        
        # add a text obect to put geometry nodes on
        labels_object = add_text(self.name + " XLabels", name=self.name + " XLabels")
        
        
        if 'XLabels' not in bpy.data.node_groups:
            append_nodetree('XLabels')
          
        geonodes = labels_object.modifiers.new('XLabels' + ' ' + self.name, type='NODES')
        geonodes.node_group = bpy.data.node_groups['XLabels']
        geonodes.node_group.nodes['Object Info'].inputs[0].default_value = self.mesh_object
        geonodes.node_group.nodes['Collection Info'].inputs[0].default_value = collection
        
        
class Bar(Scatter):
    """ Bar plot. Inerit from Scatter and add bars via Geometry Nodes """
    
    def draw(self):
        
        
        if 'Bars' not in bpy.data.node_groups:
            append_nodetree('Bars')
        
        # originial points
        scatter_object = super().draw()
        
        # make copy to put geometry nodes on
        bar_object = scatter_object.copy()
        bar_object.data = scatter_object.data.copy()
        bpy.context.collection.objects.link(bar_object) 
        
        # add geometry nodes
        geonodes = bar_object.modifiers.new('Bars' + ' ' + self.name, type='NODES')
        geonodes.node_group = bpy.data.node_groups['Bars']
        geonodes.node_group.nodes['Object Info'].inputs[0].default_value = scatter_object
        
        return scatter_object
        


class Surface(Trace):
    """ Surface trace """
    
    unnamed_surface_count = 0 # count how many unnamed surfaces have been created for consistent automatic naming.
    
    def __init__(
                    self, x=None, y=None, z=None, name="Surface", color=None,
                    mesh=True, mesh_skip='auto', mesh_thickness = .002, mesh_color=(0,0,0,1)
                ):
        
        # save input data
        self.x = np.array(x)
        self.y = np.array(y)
        self.z = np.array(z)
        
        # if unput is of mgrid form save only the axis values
        if len(self.x.shape) == 2:
            self.x = self.x[:,0]
        elif len(self.x.shape) > 2:
            raise ValueError("Too many dimensions. x should have dimension 1 for list/array or 2 for numpy's mgrid.")
        if len(self.y.shape) == 2:
            self.y = self.y[0]
        elif len(self.y.shape) > 2:
            raise ValueError("Too many dimensions. y should have dimension 1 for list/array or 2 for numpy's mgrid.")
        
        # ensure z data, if no x or y replace with integer ranges
        if not self.z.any():
            raise ValueError("No z data given")
        if not self.x.any():
            self.x = np.arange(len(z))
        if not self.y.any():
            self.y = np.arange(len(z[0]))
        
        # save data bounds
        xmin, xmax = self.x.min(), self.x.max()
        ymin, ymax = self.y.min(), self.y.max()
        zmin, zmax = self.z.min(), self.z.max()
        
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
        
        # save mesh parameters
        self.mesh = mesh # whether to create an additional mesh
        self.mesh_skip = mesh_skip 
        self.mesh_color = mesh_color
        self.mesh_thickness = mesh_thickness
        
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
        #print(f"Assigning material {material.name} color {self.color}\n Object: {object.name}\n {object.data.name}")
        
        # create mesh
        if self.mesh:
            
            # determine how many mesh lines to skip
            if self.mesh_skip == 'auto':
                self.mesh_skip = 1
            
            # create mesh material
            material = bpy.data.materials.new(self.name + ' Mesh')
            material.diffuse_color = self.mesh_color
                            
            for x in self.x[::self.mesh_skip]:
                make_mesh_curve(x=x, bevel=self.mesh_thickness, material=material)
                
            
            for y in self.y[::self.mesh_skip]:
                make_mesh_curve(y=y, bevel=self.mesh_thickness, material=material)                             
        

class Axes:
    """ Object for storing information about and drawing the axes. """
    
    def __init__(self, bounds, ticks='auto'):
        
        self.xbounds, self.ybounds, self.zbounds = bounds
        self.ticks = ticks
        self.num_ticks = (10,10,6)
    
    def update(self, bounds):
        
        self.xbounds, self.ybounds, self.zbounds = bounds
        
    def draw(self):
        
        add_box(self.xbounds, self.ybounds, self.zbounds)
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.object.data.vertices[-1].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # draw ticks
        if self.ticks:
            
            bounds = (self.xbounds, self.ybounds, self.zbounds)
            for axis in range(3):
                
                # if no input calculate ticks auomatically
                if self.ticks == 'auto':
                    ticks = automatic_ticks(*bounds[axis], num_ticks=self.num_ticks[axis])
                # otherwise take from input    
                else:
                    ticks = self.ticks[axis]
                
                add_ticks(ticks, axis, bounds=bounds) 
            
        
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
           
def map_array(input_array, output_range):
    """ Map an array of values to a desired range """
    
    # numpify
    if type(input_array) != np.ndarray: 
        input_array = np.array(input_array)
        
    # get ranges
    input_min, input_max = np.min(input_array), np.max(input_array)
    output_min, output_max = output_range
    
    return (output_max - output_min) * (input_array - input_min)/(input_max - input_min) + output_min


def scale_array(input_array, limit):
    """ Scale an array of values to be within a limiting value but preserve sign reationships """
    
    if limit <= 0:
        raise ValueError("limit must be positive")
    
    # numpify
    if type(input_array) != np.ndarray: 
        input_array = np.array(input_array)
        
    # get ranges
    input_min, input_max = np.min(input_array), np.max(input_array)
    
    if input_min < 0 and abs(input_min) > input_max:
        output_min = -limit
        output_max = input_max/abs(input_min) * limit
    else:
        output_min = input_min/input_max * limit
        output_max = limit
    
    return map_array(input_array, (output_min, output_max))

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
    
def add_text(text, name='Text', align_x='LEFT', align_y='CENTER', location=None):
    """ Add a text object or a list thereof given a string or list of strings. Optionally can add locations."""
    
    
    # handle single text object case
    if type(text) is str:
        text = [str(text)]
        location = [(0, 0, 0)] if (location is None) else [location]
        collection = False
        
    # for several cases add a collection
    else:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
        location = [(0, 0, 0)]*len(text) if (location is None) else location
            
    count = 1
    for body, loc in zip(text, location):
        
        bpy.ops.object.text_add(location=loc)
        object = bpy.context.active_object
        object.data.body = str(body)
        object.data.align_x = align_x
        object.data.align_y = align_y
        object.name = name
            
        if len(text) > 1:
            object.name += ' ' + str(count)
            count += 1
        
        # move to collection
        if collection:
            collection.objects.link(object)
            bpy.context.scene.collection.objects.unlink(object)
            
    return collection if collection else object

    

def surface_from_grid(z):
    """ Deform a flat grid (must be active) into a surface characterizad by z data. Data must match the vertex structure of the grid. """
    
    data = bpy.context.object.data
    
    xlen = len(z)
    
    for i, vert in enumerate(data.vertices):
        
        vert.co.z = z[i % xlen][int(i/xlen)]    

def surface_from_function(f, size):
    
    data = bpy.context.object.data

    for vert in data.vertices:
        
        x, y, z = vert.co
        vert.co.z = f(x+size/2, y)
        
def f(x, y):
    
    return (.05*x**2 + np.sinh(y)**2)/np.cosh(y)**4

def make_mesh_curve(x=None, y=None, bevel=0, material=None, epsilon=1.e-5):
    """ Duplicate a mesh line in a selected mesh as a sperate object. Give x or y coordinate of the mesh line. """
    
    # check for input
    if x != None:
        direction = 0
        value = x
        coordinate = 'x'
    elif y != None:
        direction = 1
        value = y
        coordinate = 'y'
    else:
        raise ValueError("No coordinate input given")
    if x != None and y != None:
        raise ValueError("Can only make curves along one direction. Give either x or y.")    
        
    # enable edge selection
    bpy.ops.object.mode_set(mode='OBJECT')
    obj = bpy.context.active_object
    bpy.ops.object.mode_set(mode='EDIT') 
    bpy.context.tool_settings.mesh_select_mode = (False, True, False) # force edges
    bpy.ops.object.mode_set(mode='OBJECT')

    # select edges which meet the criteria
    for edge in obj.data.edges:
        
        v1, v2 = edge.vertices
        v1 = obj.data.vertices[v1]
        v2 = obj.data.vertices[v2]
        
        # if the edeg is in y direction
        if abs(v1.co[direction] - v2.co[direction]) < epsilon and abs(v1.co[direction] - value) < epsilon:
            edge.select = True
        

    # duplicate selected edges
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.duplicate()
    bpy.ops.mesh.separate(type='SELECTED')
    bpy.ops.object.mode_set(mode='OBJECT')

    # rename and convert to curve
    plane, curve = bpy.context.selected_objects
    plane.select_set(False)
    bpy.context.view_layer.objects.active = curve
    curve.name = f"Curve {coordinate}={value:.1f}"
    bpy.ops.object.convert(target='CURVE')
    
    # bevel and set material
    if bevel:
        curve.data.bevel_depth = bevel
    if material:
        curve.data.materials.append(material)
    
    # select the original mesh
    bpy.context.view_layer.objects.active = obj


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
    
def add_ticks(ticks, axis, bounds=None, size = .1, offset = .2):
    
    max_length = 2
    
    if bounds == None:
        xmin, ymin, zmin = 0, 0, 0
        xmax, ymax, zmax = 0, 0, 0
    else:
        xmin, xmax =bounds[0]
        ymin, ymax =bounds[1]
        zmin, zmax =bounds[2]
    
    if axis == 0:
        rotation = (0, 0 ,pi/2)
        initial_location = [0, ymax + offset, zmin]
    elif axis == 1:
        rotation = (0, 0, pi)
        initial_location = [xmax + offset , 0, zmin]
    elif axis == 2:
        rotation = (pi/2, 0, 3*pi/4)
        initial_location = [xmax + offset/3, ymin - offset/3, 0]
        
    for tick in ticks:
        
        location = initial_location
        location[axis] = tick
        
        bpy.ops.object.text_add(location=location, rotation=rotation, scale=(1, 1, 1))
        text_data = bpy.context.object.data
        text_data.body = f"{tick:.01f}"
        text_data.size = size
        if axis:
            text_data.align_x = 'RIGHT'
        text_data.align_y = 'CENTER'
        

def append_nodetree(nodetree, filepath=''):
    """ Append a geometry nodes tree from another file """
    
    if not filepath:
        dirname = os.path.dirname(__file__)
        filepath = os.path.join(dirname, 'blendfig_assets.blend')
    else:
        dirname = os.path.dirname(filepath)
        

    bpy.ops.wm.append(
        directory=os.path.join(filepath,'NodeTree'),
        filename=nodetree
        )