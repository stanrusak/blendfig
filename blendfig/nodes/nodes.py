import bpy
import os

def append_nodetree(nodetree, filepath=''):
    """ Append a geometry nodes tree from another file """
    
    if not filepath:
        dirname = os.path.dirname(__file__)
        filepath = os.path.join(dirname, '..', 'blendfig_assets.blend')
    else:
        dirname = os.path.dirname(filepath)
        

    bpy.ops.wm.append(
        directory=os.path.join(filepath,'NodeTree'),
        filename=nodetree
        )