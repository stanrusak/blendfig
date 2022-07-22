import numpy as np
import bpy

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