from .trace import Trace
from ..bounds.bounds import Bounds
from ..geometry.geometry import add_grid, surface_from_grid, make_mesh_curve
from ..materials.colors import color_cycle
from ..tools.functions import rescale_xyz
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
        
        # get bounds
        self.bounds = Bounds._from_object(self)
        
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
        
    def draw(self, mesh=True, rescale=True):
        
        x_sub, y_sub = self.z.shape
        
        bounds = self.bounds
        if rescale:
            x, y, z = rescale_xyz(self.x, self.y, self.z)
            bounds = Bounds._from_xyz(x, y, z)
            self.bounds.rescaled = bounds
        else:
            x, y, z = self.x, self.y, self.z

        add_grid(x=bounds.x, y=bounds.y, subdivisions=(x_sub-1, y_sub-1))
        surface_from_grid(z)
        
        # rename object and mesh
        object = bpy.context.object
        object.name = self.name
        object.data.name = self.name
        
        # create and assign material
        material = bpy.data.materials.new(self.name)
        material.diffuse_color = self.color
        object.data.materials.append(material)
                
        # create mesh
        if self.mesh and mesh:
            
            # determine how many mesh lines to skip
            if self.mesh_skip == 'auto':
                self.mesh_skip = 1
            
            # create mesh material
            material = bpy.data.materials.new(self.name + ' Mesh')
            material.diffuse_color = self.mesh_color
                            
            for x_ in x[::self.mesh_skip]:
                make_mesh_curve(x=x_, bevel=self.mesh_thickness, material=material)
                
            for y_ in y[::self.mesh_skip]:
                make_mesh_curve(y=y_, bevel=self.mesh_thickness, material=material) 

    def _check_input(self):
        """ Determine input type and check for validity """

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

    def _rescale(self, initial_bounds, rescaled_bounds):
        """ Rescale data to standardize figure size """

        (xmin_i, xmax_i), (ymin_i, ymax_i), (zmin_i, zmax_i) = initial_bounds
        (xmin_r, xmax_r), (ymin_r, ymax_r), (zmin_r, zmax_r) = rescaled_bounds
        (xmin, xmax), (ymin, ymax), (zmin, zmax) = self.bounds.bounds

        x_ratio = (self.x - xmin_i)/(xmax_i - xmin_i)
        y_ratio = (self.y - ymin_i)/(ymax_i - ymin_i)
        z_ratio = (self.z - zmin_i)/(zmax_i - zmin_i)

        self._x = xmin_r + x_ratio * (xmax_r - xmin_r)
        self._y = ymin_r + y_ratio * (ymax_r - ymin_r)
        self._z = zmin_r + z_ratio * (zmax_r - zmin_r)

    def _draw_rescaled(self, initial_bounds, rescaled_bounds):

        self._rescale(initial_bounds, rescaled_bounds)

        x_sub, y_sub = self._z.shape
        xmin, xmax = self._x.min(), self._x.max()
        ymin, ymax = self._y.min(), self._y.max()
        
        add_grid(x=(xmin, xmax), y=(ymin, ymax), subdivisions=(x_sub-1, y_sub-1))
        surface_from_grid(self._z)
        
        # rename object and mesh
        object = bpy.context.object
        object.name = self.name
        object.data.name = self.name
        
        # create and assign material
        material = bpy.data.materials.new(self.name)
        material.diffuse_color = self.color
        object.data.materials.append(material)