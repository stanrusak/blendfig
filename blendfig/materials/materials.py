import bpy

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