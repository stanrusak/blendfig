from .trace import Trace
from ..geometry.geometry import add_text
from ..nodes.nodes import append_nodetree
import numpy as np
import bpy

class Scatter(Trace):
    """ Object for scatter and line plots """
    
    def __init__(self, x=None, y=None, z=None, name="Scatter"):
        

        super().__init__()
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
        
        if labels is None:
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
            
        if labels is None:
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