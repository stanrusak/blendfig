import numpy as np

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