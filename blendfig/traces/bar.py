from .scatter import Scatter
from ..nodes.nodes import append_nodetree
import bpy

class Bar(Scatter):
    """ Bar plot. Inerit from Scatter and add bars via Geometry Nodes """
    
    def draw(self, rescale=False):
        
        
        if 'Bars' not in bpy.data.node_groups:
            append_nodetree('Bars')
        
        # originial points
        scatter_object = super().draw(rescale=rescale)
        
        # make copy to put geometry nodes on
        bar_object = scatter_object.copy()
        bar_object.data = scatter_object.data.copy()
        bpy.context.collection.objects.link(bar_object)     
        
        # add geometry nodes
        geonodes = bar_object.modifiers.new('Bars' + ' ' + self.name, type='NODES')
        geonodes.node_group = bpy.data.node_groups['Bars']
        geonodes.node_group.nodes['Object Info'].inputs[0].default_value = scatter_object
        
        return scatter_object