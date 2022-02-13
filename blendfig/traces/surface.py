from .trace import Trace
from ..bounds.bounds import Bounds
from ..geometry.geometry import add_grid, surface_from_grid, make_mesh_curve
from ..materials.colors import color_cycle
import numpy as np
import bpy

class Surface(Trace):
    """ Object for drawing surfaces """
    
    unnamed_surface_count = 0 # count how many unnamed surfaces have been created for consistent automatic naming
    
    def __init__(
                    self, x=None, y=None, z=None, name="Surface", color=None,
                    mesh=True, mesh_skip='auto', mesh_thickness = .002, mesh_color=(0,0,0,1)
                ):
        
        # save input data
        self.x = np.array(x)
        self.y = np.array(y)
        self.z = np.array(z)

        # check and process input
        self._check_input()
        
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
        
    def draw(self, mesh=True):
        
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
        if self.mesh and mesh:
            
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

    def _check_input(self):

        # if input is of mgrid form save only the axis values
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
            self.x = np.arange(len(self.z))
        if not self.y.any():
            self.y = np.arange(len(self.z[0]))